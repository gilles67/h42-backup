import os, yaml, string, random, subprocess
from datetime import datetime
CONF_PATH = os.getenv("H42BACKUP_CONFPATH", "/h42backup/config")
LETTERS = string.ascii_letters
NUMBERS = string.digits

class YamlConfigFile:
    self.config = {}
    self.configfile = None
    
    def load(self):
        with open(self.configfile, 'r') as fd:
            self.config = yaml.load(fd)
            fd.close()        

    def save(self):
        with open(self.configfile, 'w') as fd:
            yaml.dump(self.config, fd)
            fd.close()

    @property
    def exists(self):
        return os.path.isfile(self.configfile) 


def password_generate(length=512):
    chars = f'{LETTERS}{NUMBERS}'
    chars = list(chars)
    random.shuffle(chars)
    password = random.choices(chars, k=length)
    password = ''.join(password)
    return password

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
            if not os.path.isfile('/h42backup/config/id_ecdsa'):
                subprocess.run(['/usr/bin/ssh-keygen', '-t', 'ed25519', '-f', '/h42backup/config/id_ecdsa', '-N', '""'], check=True)
            self.save()

    @property
    def hostname(self):
        return self.config['host']['name']

    @property
    def now(self):
        return datetime.now.strftime('%Y%m%d-%H%M%S%Z')

    def create(self, bck):
        bckname = "{0}-{1}-{2}".format(self.hostname, bck.profile, self.now)
        print("Create backup {}.".format(bckname))
        borgargs = [
            '/usr/local/bin/borg',
            '--verbose',
            '--filter', 'AME',
            '--list',
            '--stats',
            '--show-rc',
            '--compression', 'lz4',
            '--exclude-cache',
            '--progress',
            '--log-json',
            ' ',
            '::{}'.format(bckname),
        ]
        for vol in bck.volumes:
            if vol.ignore == False:
                borgargs.append(vol.dest)
        subprocess.run(borgargs, check=True)

class backupConfig(YamlConfigFile):
    
    def __init__(self, name):
        self.name = name
        self.configfile = os.path.join(CONF_PATH, self.name + "-profile.yml")
        if self.exists:
            self.load()

    def load_container(self, data):
        self.config['backup'] = data

    @property
    def profile(self):
        return self.config['backup']['profile']
    
    @property
    def volumes(self):
        return self.config['backup']['mounts']

    def getDockerVolumes(self, mode='backup'):
        vols = {'h42backup_agent_config': {'bind': CONF_PATH, 'mode': 'ro'}}
        for mount in self.volumes:
            if mount.ignore == False:
                continue
            vols[mount.name] = {'bind': mount.dest, 'mode': 'ro'}
        return vols

    def list(self):
        return self.name.ljust(30) + '| ' + self.profile

