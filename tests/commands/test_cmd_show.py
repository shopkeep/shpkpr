# third-party imports
from click.testing import CliRunner

# local imports
from shpkpr.cli import cli


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['show'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['show', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Shows detailed information for a single application.' in result.output
