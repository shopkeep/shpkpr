# stdlib imports
import functools
import json
import os

# third-party imports
import pytest
from click.testing import CliRunner

# local imports
from shpkpr.cli.entrypoint import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    return functools.partial(runner.invoke, cli)


@pytest.fixture
def json_fixture():
    def _json_fixture(name):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "fixtures", name + ".json")
        with open(path, 'r') as f:
            fixture = json.loads(f.read())
        return fixture
    return _json_fixture
