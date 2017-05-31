# stdlib imports
import functools

# third-party imports
import click
import pytest
from click.testing import CliRunner

# local imports
from shpkpr.cli import options


@pytest.fixture
def runner():
    @click.command()
    @options.marathon_client
    def _test(marathon_client, **kw):
        pass

    runner = CliRunner()
    return functools.partial(runner.invoke, _test)


def test_marathon_client_fails_with_no_args(runner):
    result = runner()
    assert result.exit_code == 2


def test_marathon_client_succeeds_with_marathon_url(runner):
    result = runner(["--marathon-url", "http://example.com"])
    assert result.exit_code == 0


def test_marathon_client_succeeds_with_marathon_url_and_basic_auth(runner):
    result = runner([
        "--marathon-url", "https://example.com",
        "--username", "someuser",
        "--password", "somepassword",
    ])

    assert result.exit_code == 0


def test_marathon_client_fails_with_marathon_url_and_basic_auth_without_ssl(runner):
    result = runner([
        "--marathon-url", "http://example.com",
        "--username", "someuser",
        "--password", "somepassword",
    ])

    assert result.exit_code == 2


def test_marathon_client_prompts_for_basic_auth_password(runner):
    result = runner([
        "--marathon-url", "https://example.com",
        "--username", "someuser",
    ], input="somepassword\n")

    assert result.exit_code == 0


def test_marathon_client_succeeds_fails_when_missing_basic_auth_username(runner):
    result = runner([
        "--marathon-url", "https://example.com",
        "--password", "somepassword",
    ])

    assert result.exit_code == 2
