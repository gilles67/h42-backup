wheels:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-distlib python3-dev python3-pip libssl-dev openssl libacl1-dev libacl1 build-essential libfuse-dev fuse pkg-config liblz4-dev libzstd-dev libxxhash-dev
	mkdir -p /opt/wheels 
	pip3 wheel -v -r /app/requirements.txt --wheel-dir=/opt/wheels

setup:
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y --no-install-recommends python3 python3-distlib python3-pip openssl libacl1 fuse liblz4-1 libzstd1 libxxhash0
	apt-get -y autoremove
	apt-get clean
	pip3 install -v --no-index --find-links=/opt/wheels -r /app/requirements.txt --break-system-packages

	apt-get -y autoremove
	apt-get -y clean
	apt-get -y autoclean

	rm -rf /opt/wheels