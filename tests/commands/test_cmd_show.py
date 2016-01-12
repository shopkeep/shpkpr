# third-party imports
import responses
from click.testing import CliRunner

# local imports
from shpkpr.cli.entrypoint import cli


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


@responses.activate
def test_task_output(runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))

    result = runner(['show'], env={
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
    })

    assert "ID:   test-app.4f923863-92a5-11e5-96b3-0e6bed2f38c7" in result.output
    assert "Host: 10.210.79.53:31001" in result.output
    assert "ID:   test-app.66c575bb-9441-11e5-8523-0a61f3a56943" in result.output
    assert "Host: 10.210.51.111:31000" in result.output
    assert result.exit_code == 0
