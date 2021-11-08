GITPACK_VERSION := $(shell git rev-list --full-history --all --abbrev-commit | head -1)
all:
#	docker build -t h42-backup/server:latest -t h42-backup/server:$(GITPACK_VERSION) ./server
	docker build -t h42-backup/agent:latest -t h42-backup/agent:$(GITPACK_VERSION) ./agent
