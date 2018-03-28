.PHONY: build-test clean clean.build clean.pyc clean.test docs.watch docs help test.2.7 test.3.4 test.3.5 test.3.6 test.pypy test.integration test


default: help

help: ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -Ee 's/([a-z.]*):[^#]*##(.*)/\1##\2/' | sort | column -t -s "##"


docs: ## Generate Sphinx HTML documentation
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

docs.watch: docs ## Watch for file changes and regenerate documentation as required
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

build-test:
	docker build -f Dockerfile.test -t shpkpr-test .

# User-defined function to allow easy running of our tests inside Docker
docker-test = docker run -i -v `pwd`:/src:ro -v /var/run/docker.sock:/var/run/docker.sock $(1) --rm shpkpr-test $(2)

test: clean build-test ## Run tests against all supported Python versions (2.7, 3.4, 3.5, 3.6 and pypy) inside Docker
	$(call docker-test)

test.2.7: clean build-test ## Run Python 2.7 tests inside Docker
	$(call docker-test,,tox -e py27-lowest -e py27-current)

test.3.4: clean build-test ## Run Python 3.4 tests inside Docker
	$(call docker-test,,tox -e py34-lowest -e py34-current)

test.3.5: clean build-test ## Run Python 3.5 tests inside Docker
	$(call docker-test,,tox -e py35-lowest -e py35-current)

test.3.6: clean build-test ## Run Python 3.6 tests inside Docker
	$(call docker-test,,tox -e py36-lowest -e py36-current)

test.pypy: clean build-test ## Run PyPy 2 tests inside Docker
	$(call docker-test,,tox -e pypy-lowest,pypy-current)

test.integration: clean build-test ## Run integration tests inside Docker
	$(shell env | grep SHPKPR > .env.integration)
	$(call docker-test,--env-file .env.integration,tox -e integration)


clean: clean.build clean.pyc clean.test ## Remove all build, test, coverage and Python artifacts

clean.build: ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean.pyc: ## Remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean.test: ## Remove test and coverage artifacts
	rm -fr .cache/
	rm -fr .tox/
	rm -f .coverage
	rm -f .env.integration
	rm -fr htmlcov/
