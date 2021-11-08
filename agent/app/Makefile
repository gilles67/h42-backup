all:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-dev python3-pip libssl-dev openssl libacl1-dev libacl1 build-essential libfuse-dev fuse pkg-config
	apt-get -y autoremove
	apt-get clean
	pip3 install -r /app/requirements.txt

	chmod a+x /app/h42-backup-agent
	mkdir /app/config

