wheels:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-distutils python3-dev python3-pip libssl-dev openssl libacl1-dev libacl1 build-essential libfuse-dev fuse pkg-config
	mkdir -p /opt/wheels 
	pip3 wheel -v -r /app/requirements.txt --wheel-dir=/opt/wheels

setup:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-distutils python3-pip openssl libacl1 fuse
	apt-get -y autoremove
	apt-get clean
	pip3 install -v --no-index --find-links=/opt/wheels -r /app/requirements.txt

	apt-get -y autoremove
	apt-get -y clean
	apt-get -y autoclean

	rm -rf /opt/wheels

	useradd -u 5000 -N -g 65534 borg
	mkdir -p /home/borg/.ssh
	chown -R borg:nogroup /home/borg
	chmod -R 700 /home/borg

	mkdir -p /backup
	chown -R borg:nogroup /backup
