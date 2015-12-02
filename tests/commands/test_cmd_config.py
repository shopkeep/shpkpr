# third-party imports
from click.testing import CliRunner

# local imports
from shpkpr.cli import cli


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['config'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Manage application configuration.' in result.output


def test_list_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'list'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_list_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'list', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'List application configuration.' in result.output


def test_set_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'set'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_set_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'set', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Set application configuration.' in result.output


def test_unset_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'unset'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_unset_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'unset', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Unset application configuration.' in result.output
