# stdlib imports
import json

# third-party imports
import responses
import yaml
from click.testing import CliRunner

# local imports
from shpkpr.cli.entrypoint import cli


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(cli, ['apps', 'show'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['apps', 'show', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Show detailed information for one or more applications.' in result.output


@responses.activate
def test_show_single_app(runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))

    result = runner(['apps', 'show'], env={
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
    })
    assert result.exit_code == 0

    parsed_payload = json.loads(result.output)
    assert isinstance(parsed_payload, dict)
    assert parsed_payload["id"] == "/test-app"


@responses.activate
def test_show_multiple_apps(runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps',
                  status=200,
                  json=json_fixture("valid_apps"))

    result = runner(['apps', 'show'], env={
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
    })
    assert result.exit_code == 0

    parsed_payload = json.loads(result.output)
    assert isinstance(parsed_payload, list)

    sorted_app_ids = sorted([x.get('id') for x in parsed_payload])
    assert sorted_app_ids == ["/test-app-a", "/test-app-b", "/test-app-c"]


@responses.activate
def test_show_format_json(runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))

    result = runner(['apps', 'show'], env={
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
    })
    assert result.exit_code == 0

    parsed_payload = json.loads(result.output)
    assert isinstance(parsed_payload, dict)


@responses.activate
def test_show_format_yaml(runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))

    result = runner(['apps', 'show'], env={
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
    })
    assert result.exit_code == 0

    parsed_payload = yaml.load(result.output)
    assert isinstance(parsed_payload, dict)
