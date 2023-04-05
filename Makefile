GITPACK_VERSION := $(shell git rev-list --full-history --all --abbrev-commit | head -1)
agent:
	docker build -t gilles67/h42-backup-server:latest -t gilles67/h42-backup-server:$(GITPACK_VERSION) ./server
server:
	docker build -t gilles67/h42-backup-agent:latest -t gilles67/h42-backup-agent:$(GITPACK_VERSION) ./agent
all: agent server
