import os
import string
import random
import subprocess
import logging
import threading
from datetime import datetime

import yaml

CONF_PATH = os.getenv("H42BACKUP_CONFPATH", "/h42backup/config")
LETTERS = string.ascii_letters
NUMBERS = string.digits

def password_generate(length=512):
    chars = f'{LETTERS}{NUMBERS}'
    chars = list(chars)
    random.shuffle(chars)
    password = random.choices(chars, k=length)
    password = ''.join(password)
    return password


class LogPipe(threading.Thread):

    def __init__(self, level=logging.INFO):
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            logging.log(self.level, line.strip('\n'))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)

class YamlConfigFile:
    config = {}
    configfile = None

    def load(self):
        yload = yaml.Loader
        if yaml.CLoader:
            yload = yaml.CLoader
        with open(self.configfile, 'r', encoding="utf-8") as fd:
            self.config = yaml.load(fd, Loader=yload)
            fd.close()

    def save(self):
        ydump = yaml.Dumper
        if yaml.CDumper:
            ydump = yaml.CDumper
        with open(self.configfile, 'w', encoding="utf-8") as fd:
            yaml.dump(self.config, fd, Dumper=ydump)
            fd.close()

    @property
    def exists(self):
        return os.path.isfile(self.configfile) 

class borgConfig(YamlConfigFile):
    def __init__(self):
        self.configfile = os.path.join(CONF_PATH,"borg.yml")
        if self.exists:
            self.load()
        else:
            self.config['borg'] = {}
            self.config['borg']['repo'] = os.getenv('H42BACKUP_REPO', 'ssh://localhost:22/root/')
            self.config['borg']['passphrase'] = os.getenv('H42BACKUP_PASSPHRASE', password_generate())
            self.config['host'] = {}
            self.config['host']['name'] = os.getenv('H42BACKUP_HOSTNAME', 'myhost')
            if not os.path.isfile('/root/.ssh/id_rsa'):
                subprocess.run(['/usr/bin/ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', '/root/.ssh/id_rsa', '-N', '""'], check=True)
            self.save()

    @property
    def hostname(self):
        return self.config['host']['name']

    @property
    def repo(self):
        return self.config['borg']['repo']

    @property
    def passphrase(self):
        return self.config['borg']['passphrase']

    @property
    def now(self):
        return datetime.now().strftime('%Y%m%d')

    @property
    def publicKey(self):
        publickey = None
        with open('/root/.ssh/id_rsa.pub', 'r', encoding="utf-8") as fd:
            publickey = fd.readlines()[0].strip()
            fd.close()
        return publickey

    def create(self, bck):
        cmdenv = os.environ.copy()
        cmdenv.update(BORG_REPO=self.repo, BORG_PASSPHRASE=self.passphrase)
        bckname = f"{self.hostname}-{bck.archive}-{self.now}"
        print(f"Create backup {bckname}.")
        logging.basicConfig(level=logging.INFO,filename=f"{CONF_PATH}/logs/{bckname}.log")

        borgargs = [
            '/usr/local/bin/borg',
            'create',
            '--verbose',
            '--filter=AME',
            '--list',
            '--stats',
            '--show-rc',
            '--compression=lz4',
            '--exclude-cache',
            '--progress',
            f'::{bckname}',
        ]
        for vol in bck.volumes:
            if 'ignore' in vol and not vol['ignore']:
                borgargs.append(vol['dest'])

        lpipe = LogPipe()
        with subprocess.Popen(borgargs, env=cmdenv, stdout=lpipe, stderr=lpipe):
            lpipe.close()

    def initRepo(self):
        cmdenv = os.environ.copy()
        cmdenv.update(BORG_REPO=self.repo, BORG_PASSPHRASE=self.passphrase)
        borgargs = [
            '/usr/local/bin/borg',
            'init',
            '--encryption', 'repokey'
        ]
        subprocess.run(borgargs, check=True, env=cmdenv)
        

class backupConfig(YamlConfigFile):
    
    def __init__(self, name):
        self.name = name
        self.configfile = os.path.join(CONF_PATH, self.name + "-profile.yml")
        self.config['name'] = self.name
        if self.exists:
            self.load()

    def load_container(self, data):
        self.config['backup'] = data

    @property
    def profile(self):
        return self.config['backup']['profile']

    @property
    def archive(self):
        if self.profile == "volume":
            name = self.name.replace('.','-')
            return f"{name}-{self.profile}"
        else:
            return self.name.replace('.','-')
    
    @property
    def volumes(self):
        return self.config['backup']['mounts']

    def getDockerVolumes(self, mode='backup'):
        vols = {'h42backup_agent_config': {'bind': CONF_PATH, 'mode': 'ro'}, 'h42backup_agent_root': {'bind': '/root', 'mode': 'ro'}}
        for mount in self.volumes:
            print(mount)
            if 'ignore' in mount and not mount['ignore']:
                continue
            if 'name' in mount:
                vols[mount['name']] = {'bind': mount['dest'], 'mode': 'ro'}
        return vols

    def list(self):
        return self.name.ljust(30) + '| ' + self.profile

