wheels:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-distutils python3-dev python3-pip libssl-dev openssl libacl1-dev libacl1 build-essential libfuse-dev fuse pkg-config openssh-client
	mkdir -p /opt/wheels 
	pip3 wheel -v -r /h42backup/requirements.txt --wheel-dir=/opt/wheels

setup:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-distutils python3-pip openssl libacl1 fuse openssh-client
	apt-get -y autoremove
	apt-get clean
	pip3 install -v --no-index --find-links=/opt/wheels -r /h42backup/requirements.txt

	apt-get -y autoremove
	apt-get -y clean
	apt-get -y autoclean

	rm -rf /opt/wheels

	chmod a+x /h42backup/h42-backup-agent
	chmod a+x /h42backup/inf-loop
	mkdir /h42backup/config
