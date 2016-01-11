# third-party imports
import mock
import responses


def test_no_args(runner):
    result = runner(['deploy'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['deploy', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Deploy application from template.' in result.output


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_no_force(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_DOCKER_EXPOSED_PORT': '8080',
        'SHPKPR_DEPLOY_DOMAIN': 'mydomain.com',
    }
    result = runner(['deploy', '--template', 'tests/test.json.tmpl', 'RANDOM_LABEL=some_value'], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_force(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app?force=true',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_DOCKER_EXPOSED_PORT': '8080',
        'SHPKPR_DEPLOY_DOMAIN': 'mydomain.com',
    }
    result = runner(['deploy', '--template', 'tests/test.json.tmpl', '--force', 'RANDOM_LABEL=some_value'], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_multiple_templates(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_APPLICATION_2': 'test-app-2',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_DOCKER_EXPOSED_PORT': '8080',
        'SHPKPR_DEPLOY_DOMAIN': 'mydomain.com',
        'SHPKPR_RANDOM_LABEL': 'some_value',
    }
    result = runner(['deploy', '--template', 'tests/test.json.tmpl', '--template', 'tests/test-2.json.tmpl'], env=env)

    assert result.exit_code == 0
