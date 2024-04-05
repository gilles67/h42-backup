import os
import os.path
import string
import random
import subprocess
import logging
import threading
from datetime import datetime

import yaml

BASE_BORG = os.getenv("BORG_BASEDIR", "/h42backup/backup")
CONF_PATH = os.getenv("H42BACKUP_CONFPATH", "/h42backup/config")
LOG_PATH = os.path.join(CONF_PATH,'logs')
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
        self.fd_read, self.fd_write = os.pipe()
        self.pipe_reader = os.fdopen(self.fd_read)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fd_write

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipe_reader.readline, ''):
            logging.log(self.level, line.strip('\n'))

        self.pipe_reader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fd_write)

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
        if not os.path.isdir(BASE_BORG):
            os.mkdir(BASE_BORG)
        if not os.path.isdir(LOG_PATH):
            os.mkdir(LOG_PATH)
        cmdenv = os.environ.copy()
        cmdenv.update(BORG_REPO=self.repo, BORG_PASSPHRASE=self.passphrase, BORG_BASE_DIR=BASE_BORG)
        logname = f"{self.hostname}-{bck.archive}"
        bckname = f"{logname}-{self.now}"

        print(f"Create backup {bckname}.")
        logging.basicConfig(level=logging.INFO,
                            filename=f"{LOG_PATH}/{logname}.log",
                            format="%(asctime)s [%(levelname)s]: %(message)s",
                            datefmt="%Y-%m-%dT%H:%M:%S")
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
                borgargs.append(vol['dst'])
        lpipe = LogPipe()

        # Main backup exec
        try:
            with subprocess.Popen(borgargs, env=cmdenv, stdout=lpipe, stderr=lpipe):
                lpipe.close()
        except Exception as err:
            logging.error(err)

        # Post backup exec
        try:
            if bck.profile == "mariadb":
                logging.info("Purge mariadb backup folder")
                subprocess.run("/bin/rm -r /var/backup/*", check=True)
        except Exception as err:
            logging.error(err)

        bck.unlock()

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
        self.lockfile = os.path.join(CONF_PATH, self.name + ".lock")
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

    @property
    def is_lock(self):
        return os.path.isfile(self.lockfile)

    def getDockerVolumes(self):
        vols = self.volumes.copy()
        vols.append({'type': 'volume', 'name': 'h42backup_agent_config', 'dst': CONF_PATH, 'ignore': False, 'mode': 'rw'})
        vols.append({'type': 'volume', 'name': 'h42backup_agent_root', 'dst': '/root', 'ignore': False, 'mode': 'ro'})
        return vols

    def lock(self, container_name):
        with open(self.lockfile, mode="w", encoding="utf-8") as f:
            f.write(container_name)
            f.close()

    def unlock(self):
        if self.is_lock:
            os.remove(self.lockfile)

    def list(self):
        if self.is_lock:
            return self.name.ljust(30) + '| ' + self.profile + ' (locked)'
        else:
            return self.name.ljust(30) + '| ' + self.profile
