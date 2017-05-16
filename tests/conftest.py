# stdlib imports
import json
import os

# third-party imports
import pytest


@pytest.fixture
def file_fixture():
    def _file_fixture(name):
        here = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(here, "fixtures", name)
        with open(path, 'r') as f:
            fixture = f.read()
        return fixture
    return _file_fixture


@pytest.fixture
def json_fixture(file_fixture):
    def _json_fixture(name):
        return json.loads(file_fixture(name + ".json"))
    return _json_fixture
