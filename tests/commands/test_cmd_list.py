# third-party imports
from click.testing import CliRunner

# local imports
from shpkpr.cli import cli


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['list', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Lists all applications currently deployed to marathon.' in result.output
