# third-party imports
import mock
import responses


def test_no_args(runner):
    result = runner(['scale'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['scale', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Scale application resources to specified levels.' in result.output


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_no_force(mock_deployment_wait, runner, json_fixture):
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
    result = runner(['scale', '--application', 'test-app', '--cpus', '0.25'], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_force(mock_deployment_wait, runner, json_fixture):
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
    result = runner(['scale', '--application', 'test-app', '--cpus', '0.25', '--force'], env=env)

    assert result.exit_code == 0
