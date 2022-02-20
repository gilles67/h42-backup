import os, configparser, string, random
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
        self.config = configparser.ConfigParser()
        self.configfile = os.path.join(CONF_PATH, self.name + "borg.ini")
        if self.exists:
            self.config.read(self.configfile)
        else:
            self.config['borg']['repo'] = os.getenv('H42BACKUP_REPO', 'ssh://localhost:22/root/')
            self.config['borg']['passphrase'] = os.getenv('H42BACKUP_PASSPHRASE', password_generate())
            self.config['host']['name'] = os.getenv('H42BACKUP_HOSTNAME', 'myhost')
            if not os.path.isfile('/h42backup/config/id_ecdsa'):
                os.system('ssh-keygen -t ed25519 -f /h42backup/config/id_ecdsa -N  ""')
            self.save()

    def save(self):
        with open(self.configfile, 'w') as fd:
            self.config.write(fd)
            fd.close()

    @property
    def exists(self):
        return os.path.isfile(self.configfile) 




class backupConf:
    
    def __init__(self, name):
        self.name = name
        self.config = configparser.ConfigParser()
        self.configfile = os.path.join(CONF_PATH, self.name + "-profile.ini")
        if self.exists:
            self.config.read(self.configfile)

    def load_container(self, data):
        self.config['backup'] = data

    def save(self):
        with open(self.configfile, 'w') as fd:
            self.config.write(fd)
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

    def getVolumes(self, mode='backup'):
        vols = {'h42backup_agent_config': {'bind': CONF_PATH, 'mode': 'ro'}}
        for mount in self.volumes:
            if mount.ignore == False:
                continue
            vols.update(mount.name={'bind': mount.dest, 'mode': 'ro'})
        return vols

    def list(self):
        return self.name.ljust(30) + '| ' + self.profile

