.PHONY: help test.2.7 test.3.3 test.3.4 test.3.5 test.pypy test


default: help

help: ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -Ee 's/([a-z.]*):[^#]*##(.*)/\1##\2/' | sort | column -t -s "##"


test: test.2.7 test.3.3 test.3.4 test.3.5 test.pypy ## Run tests against all supported Python versions (2.7, 3.3, 3.4, 3.5 and pypy) inside Docker

test.2.7: ## Run Python 2.7 tests inside Docker
	docker build -f dockerfiles/Dockerfile-python-2.7 -t shpkpr-2.7 . && docker run -ti shpkpr-2.7 tox -e py27

test.3.3: ## Run Python 3.3 tests inside Docker
	docker build -f dockerfiles/Dockerfile-python-3.3 -t shpkpr-3.3 . && docker run -ti shpkpr-3.3 tox -e py33

test.3.4: ## Run Python 3.4 tests inside Docker
	docker build -f dockerfiles/Dockerfile-python-3.4 -t shpkpr-3.4 . && docker run -ti shpkpr-3.4 tox -e py34

test.3.5: ## Run Python 3.5 tests inside Docker
	docker build -f dockerfiles/Dockerfile-python-3.5 -t shpkpr-3.5 . && docker run -ti shpkpr-3.5 tox -e py35

test.pypy: ## Run PyPy 2 tests inside Docker
	docker build -f dockerfiles/Dockerfile-pypy-2-4.0 -t shpkpr-pypy-2 . && docker run -ti shpkpr-pypy-2 tox -e pypy
