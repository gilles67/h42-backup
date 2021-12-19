import os, configparser
CONF_PATH = os.getenv("H42BACKUP_CONFPATH", "/h42backup/config")


class backupConf:
    
    def __init__(self, name):
        self.name = name
        self.config = configparser.ConfigParser()
        self.configfile = os.path.join(CONF_PATH, self.name + "-profile.ini")
        if os.path.isfile(self.configfile):
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

    def list(self):
        return self.name.ljust(30) + '| ' + self.profile


