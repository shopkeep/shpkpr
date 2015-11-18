.PHONY: clean clean.build clean.pyc clean.test help test.2.7 test.3.3 test.3.4 test.3.5 test.pypy test


default: help

help: ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -Ee 's/([a-z.]*):[^#]*##(.*)/\1##\2/' | sort | column -t -s "##"


test: test.2.7 test.3.3 test.3.4 test.3.5 test.pypy ## Run tests against all supported Python versions (2.7, 3.3, 3.4, 3.5 and pypy) inside Docker

# User-defined function to allow easy running of our tests inside Docker
test_with_docker = docker build -f $(1) -t $(2) . && docker run -ti $(2) tox -e $(3)

test.2.7: ## Run Python 2.7 tests inside Docker
	$(call test_with_docker,Dockerfile,shpkpr-2.7,py27)

test.3.3: ## Run Python 3.3 tests inside Docker
	$(call test_with_docker,dockerfiles/Dockerfile-python-3.3,shpkpr-3.3,py33)

test.3.4: ## Run Python 3.4 tests inside Docker
	$(call test_with_docker,dockerfiles/Dockerfile-python-3.4,shpkpr-3.4,py34)

test.3.5: ## Run Python 3.5 tests inside Docker
	$(call test_with_docker,dockerfiles/Dockerfile-python-3.5,shpkpr-3.5,py35)

test.pypy: ## Run PyPy 2 tests inside Docker
	$(call test_with_docker,dockerfiles/Dockerfile-pypy-2-4.0,shpkpr-pypy-2,pypy)


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
	rm -fr htmlcov/
