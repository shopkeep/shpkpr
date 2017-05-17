# stdlib imports
import functools

# third-party imports
import pytest
from click.testing import CliRunner

# local imports
from shpkpr.cli.entrypoint import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    return functools.partial(runner.invoke, cli)
