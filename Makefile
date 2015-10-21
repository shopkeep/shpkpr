
.PHONY: help test run artifact artifact.tag artifact.push deploy

default: help

help: ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -Ee 's/([a-z.]*):[^#]*##(.*)/\1##\2/' | sort | column -t -s "##"

CS_DOCKER_IMAGE_NAME = deploytool
CS_GIT_SHA = $(shell git rev-parse HEAD)

# CS_GIT_BRANCH is special cased because of the way Jenkins handles git
# repositories. When Jenkins checks out a commit the branch is left in a
# "detached head" state and thus it's not possible to determine the branch
# name using the same method we use locally.
ifndef GIT_BRANCH
	CS_GIT_BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
else
	CS_GIT_BRANCH = $(shell echo $$GIT_BRANCH | cut -d / -f 2)
endif

# check if the git repository contains any untracked or changed files. If it
# does then we set a "dirty tag" that will be appended to any container tags
# or image names when built to indicate that the artifact was not built from
# a pristine git checkout.
IS_REPO_DIRTY = $(shell git diff --shortstat 2> /dev/null | tail -n1)
ifeq ($(strip $(IS_REPO_DIRTY)),)
	CS_DIRTY_TAG =
else
	CS_DIRTY_TAG= -dirty
endif

ifndef CONTAINERIZED
test: artifact.tag ## Run the unit tests in a Docker container against a Docker based database
	$(info running unit test containers)
	docker run -ti -e "CONTAINERIZED=true" --entrypoint="make" $(CS_DOCKER_REGISTRY_STAGING)/$(CS_DOCKER_IMAGE_NAME):$(CS_GIT_BRANCH)-$(CS_GIT_SHA)$(CS_DIRTY_TAG) test
else
test: ## (with "CONTAINERIZED=true") Run the unit tests directly via go
	@echo "WARNING: deploytool does not have any tests yet."
endif

artifact: artifact.push ## Build, tag and push a Docker image to the registry

artifact.tag: ## Build and tag a docker image for the current git revision
	docker build -t $(CS_DOCKER_REGISTRY_STAGING)/$(CS_DOCKER_IMAGE_NAME):$(CS_GIT_BRANCH)-$(CS_GIT_SHA)$(CS_DIRTY_TAG) .

artifact.push: artifact.tag ## Push a docker image for the current git revision to the registry
	docker push $(CS_DOCKER_REGISTRY_STAGING)/$(CS_DOCKER_IMAGE_NAME):$(CS_GIT_BRANCH)-$(CS_GIT_SHA)$(CS_DIRTY_TAG)
