# third-party imports
from click.testing import CliRunner

# local imports
from shpkpr.cli.entrypoint import cli


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['logs'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['logs', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Tail a file in a mesos task\'s sandbox.' in result.output
