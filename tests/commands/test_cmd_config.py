# third-party imports
import mock
import responses


def test_no_args(runner):
    result = runner(['config'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['config', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Manage application configuration.' in result.output


def test_list_no_args(runner):
    result = runner(['config', 'list'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_list_help(runner):
    result = runner(['config', 'list', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'List application configuration.' in result.output


def test_set_no_args(runner):
    result = runner(['config', 'set'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_set_help(runner):
    result = runner(['config', 'set', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Set application configuration.' in result.output


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_set_no_force(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080"}
    result = runner(['config', 'set', '--application', 'test-app', 'MYKEY=MYVAL'], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_set_force(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app?force=true',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080"}
    result = runner(['config', 'set', '--application', 'test-app', '--force', 'MYKEY=MYVAL'], env=env)

    assert result.exit_code == 0


def test_unset_no_args(runner):
    result = runner(['config', 'unset'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_unset_help(runner):
    result = runner(['config', 'unset', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Unset application configuration.' in result.output


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_unset_no_force(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080"}
    result = runner(['config', 'unset', '--application', 'test-app', 'MYKEY'], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_unset_force(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=json_fixture("valid_app"))
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app?force=true',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080"}
    result = runner(['config', 'unset', '--application', 'test-app', '--force', 'MYKEY'], env=env)

    assert result.exit_code == 0
