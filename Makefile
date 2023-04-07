GITPACK_VERSION := $(shell git rev-list --full-history --all --abbrev-commit | head -1)

all:
	docker build -t gilles67/h42-backup-server:latest -t gilles67/h42-backup-server:$(GITPACK_VERSION) ./server
	docker build -t gilles67/h42-backup-agent:latest -t gilles67/h42-backup-agent:$(GITPACK_VERSION) ./agent
	docker push gilles67/h42-backup-server:latest 
	docker push gilles67/h42-backup-server:$(GITPACK_VERSION)
	docker push gilles67/h42-backup-agent:latest
	docker push gilles67/h42-backup-agent:$(GITPACK_VERSION)
