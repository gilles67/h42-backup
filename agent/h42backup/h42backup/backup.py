import os, yaml, string, random, subprocess
from datetime import datetime
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

class borgConf:
    def __init__(self):
        self.config = {}
        self.configfile = os.path.join(CONF_PATH,"borg.yml")
        if self.exists:
            with open(self.configfile, 'r') as fd:
                self.config = yaml.load(fd)
                fd.close()
        else:
            self.config['borg'] = {}
            self.config['borg']['repo'] = os.getenv('H42BACKUP_REPO', 'ssh://localhost:22/root/')
            self.config['borg']['passphrase'] = os.getenv('H42BACKUP_PASSPHRASE', password_generate())
            self.config['host'] = {}
            self.config['host']['name'] = os.getenv('H42BACKUP_HOSTNAME', 'myhost')
            if not os.path.isfile('/h42backup/config/id_ecdsa'):
                subprocess.run(['/usr/bin/ssh-keygen', '-t', 'ed25519', '-f', '/h42backup/config/id_ecdsa', '-N', '""'], check=True)
            self.save()

    def save(self):
        with open(self.configfile, 'w') as fd:
            yaml.dump(self.config, fd)
            fd.close()

    @property
    def hostname(self):
        return self.config['host']['name']

    @property
    def now(self):
        return datetime.now.strftime('%Y%m%d-%H%M%S%Z')

    @property
    def exists(self):
        return os.path.isfile(self.configfile) 

    def create(self, bck):
        print("Create backup {0}-{1}-{2} ".format(self.hostname, bck.profile, self.now))


class backupConf:
    
    def __init__(self, name):
        self.name = name
        self.config = configparser.ConfigParser()
        self.configfile = os.path.join(CONF_PATH, self.name + "-profile.yml")
        if self.exists:
            with open(self.configfile, 'r') as fd:
                self.config = yaml.load(fd)
                fd.close()

    def load_container(self, data):
        self.config['backup'] = data

    def save(self):
        with open(self.configfile, 'w') as fd:
            yaml.dump(self.config, fd)
            fd.close()

    @property
    def profile(self):
        return self.config['backup']['profile']
    
    @property
    def volumes(self):
        return self.config['backup']['mounts']

    @property
    def exists(self):
        return os.path.isfile(self.configfile)

    def getDockerVolumes(self, mode='backup'):
        vols = {'h42backup_agent_config': {'bind': CONF_PATH, 'mode': 'ro'}}
        for mount in self.volumes:
            if mount.ignore == False:
                continue
            vols[mount.name] = {'bind': mount.dest, 'mode': 'ro'}
        return vols

    def list(self):
        return self.name.ljust(30) + '| ' + self.profile

