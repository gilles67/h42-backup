all:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-dev python3-pip libssl-dev openssl libacl1-dev libacl1 build-essential libfuse-dev fuse pkg-config openssh-client
	apt-get -y autoremove
	apt-get clean
	pip3 install -v -r /h42backup/requirements.txt

	apt-get remove -y python3-pip
	apt-get purge -y python3-dev python3-pip libssl-dev libacl1-dev build-essential libfuse-dev
	apt-get -y autoremove
	apt-get -y clean
	apt-get -y autoclean

	chmod a+x /h42backup/h42-backup-agent
	chmod a+x /h42backup/inf-loop
	mkdir /h42backup/config

