import os, os.path, string
import subprocess, logging, threading
from datetime import datetime

LOG_PATH = os.getenv("LOG_PATH", "/var/backup/")

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


class borgTask():

    _lockfile = None

    def __init__(self):
        self._lockfile = os.getenv("LOCK_FILE", "/var/backup/backup.lock")

    @property
    def now(self):
        return datetime.now().date().isoformat()

    @property
    def is_lock(self):
        return os.path.isfile(self._lockfile)

    def lock(self):
        if self.is_lock:
            raise Exception('Backup lock exists.')
        with open(self._lockfile, mode="w", encoding="utf-8") as f:
            f.write(self.now)
            f.close()

    def unlock(self):
        if self.is_lock:
            os.remove(self._lockfile)

    def create(self):
        self.lock()
        cmdenv = os.environ.copy()
        logname = f"backup-{self.now}"
        bckname = f"{self.now}"

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
            '/mnt'
        ]
        lpipe = LogPipe()

        # Main backup exec
        try:
            with subprocess.Popen(borgargs, env=cmdenv, stdout=lpipe, stderr=lpipe):
                lpipe.close()
        except Exception as err:
            logging.error(err)

        self.unlock()


if __name__ == '__main__':

    try: 
        backup = borgTask()
        backup.create()
    except Exception as err:
        print(err)
        exit(1)
