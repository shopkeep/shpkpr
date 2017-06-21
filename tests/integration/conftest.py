# stdlib imports
import functools
import os

# third-party imports
import pytest
from click.testing import CliRunner

# local imports
from shpkpr.cli.entrypoint import cli


@pytest.fixture(scope="session")
def env():
    # read the required environment variables into a dictionary and assert
    # that they're set appropriately
    env = {
        "SHPKPR_MARATHON_APP_ID": os.environ.get("SHPKPR_MARATHON_APP_ID", None),
        "SHPKPR_MARATHON_URL": os.environ.get("SHPKPR_MARATHON_URL", None),
        "SHPKPR_MARATHON_LB_URL": os.environ.get("SHPKPR_MARATHON_LB_URL", None),
        "SHPKPR_APPLICATION": os.environ.get("SHPKPR_APPLICATION", None),
        "SHPKPR_DEPLOYMENT_GROUP": os.environ.get("SHPKPR_DEPLOYMENT_GROUP", None),
        "SHPKPR_DOCKER_REPOTAG": os.environ.get("SHPKPR_DOCKER_REPOTAG", None),
        "SHPKPR_DOCKER_EXPOSED_PORT": os.environ.get("SHPKPR_DOCKER_EXPOSED_PORT", None),
        "SHPKPR_DEPLOY_DOMAIN": os.environ.get("SHPKPR_DEPLOY_DOMAIN", None),
        "SHPKPR_CHRONOS_URL": os.environ.get("SHPKPR_CHRONOS_URL", None),
        "SHPKPR_CHRONOS_VERSION": os.environ.get("SHPKPR_CHRONOS_VERSION", None),
        "SHPKPR_VAULT_ADDR": os.environ.get("SHPKPR_VAULT_ADDR", None),
        "SHPKPR_VAULT_TOKEN": os.environ.get("SHPKPR_VAULT_TOKEN", None),
    }
    assert None not in env.values()
    return env


@pytest.fixture
def runner():
    runner = CliRunner()
    return functools.partial(runner.invoke, cli)
