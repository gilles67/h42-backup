all:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-dev python3-pip libssl-dev openssl libacl1-dev libacl1 build-essential libfuse-dev fuse pkg-config
	apt-get -y autoremove
	apt-get clean
	pip3 install -v -r /h42backup/requirements.txt

	chmod a+x /h42backup/h42-backup-agent
	mkdir /h42backup/config

