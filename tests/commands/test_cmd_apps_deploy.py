# third-party imports
import mock
import responses


def test_no_args(runner):
    result = runner(['apps', 'deploy'])

    assert result.exit_code == 2
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['apps', 'deploy', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Deploy one or more applications to Marathon.' in result.output


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
    _tmpl_path = "tests/fixtures/templates/marathon/test.json.tmpl"
    result = runner(['apps', 'deploy', '--template', _tmpl_path, 'RANDOM_LABEL=some_value'], env=env)

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
    _tmpl_path = "tests/fixtures/templates/marathon/test.json.tmpl"
    result = runner(['apps', 'deploy', '--template', _tmpl_path, '--force', 'RANDOM_LABEL=some_value'], env=env)

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
    _tmpl_path = "tests/fixtures/templates/marathon/test.json.tmpl"
    _tmpl_path_2 = "tests/fixtures/templates/marathon/test-2.json.tmpl"
    result = runner(['apps', 'deploy', '--template', _tmpl_path, '--template', _tmpl_path_2], env=env)

    assert result.exit_code == 0


@responses.activate
def test_dry_run(runner, json_fixture):
    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_DOCKER_EXPOSED_PORT': '8080',
    }
    _tmpl_path = "tests/fixtures/templates/marathon/test.json.tmpl"
    result = runner(['apps', 'deploy', '--dry-run', '--template', _tmpl_path, 'RANDOM_LABEL=some_value'], env=env)

    assert result.exit_code == 0
    assert '--dry-run' in result.output


@responses.activate
def test_dry_run_fail(runner, json_fixture):
    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
    }
    _tmpl_path = "tests/fixtures/templates/marathon/test.json.tmpl"
    result = runner(['apps', 'deploy', '--dry-run', '--template', _tmpl_path, 'RANDOM_LABEL=some_value'], env=env)

    assert not result.exit_code == 0


@responses.activate
def test_strategy_bluegreen_fails_without_marathon_lb(runner):
    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_DOCKER_EXPOSED_PORT': '8080',
        'SHPKPR_DEPLOYMENT_GROUP': 'test',
        'SHPKPR_DEPLOY_DOMAIN': 'test.com',
    }
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen.json.tmpl"
    result = runner(['apps', 'deploy', '--strategy', 'bluegreen', '--template', _tmpl_path], env=env)

    assert result.exit_code == 2
    assert 'Missing option "--marathon_lb_url".' in result.output


@responses.activate
def test_strategy_bluegreen(runner):
    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_MARATHON_LB_URL': "http://marathon-lb.somedomain.com:8080",
        'SHPKPR_APPLICATION': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_DOCKER_EXPOSED_PORT': '8080',
        'SHPKPR_DEPLOYMENT_GROUP': 'test',
        'SHPKPR_DEPLOY_DOMAIN': 'test.com',
    }
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen.json.tmpl"
    result = runner(['apps', 'deploy', '--dry-run', '--strategy', 'bluegreen', '--template', _tmpl_path], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_default_template(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_MARATHON_APP_ID': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
    }
    result = runner(['apps', 'deploy'], env=env)

    assert result.exit_code == 0


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.wait')
def test_default_template_labels(mock_deployment_wait, runner, json_fixture):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=json_fixture("deployment"),
                  match_querystring=True)
    mock_deployment_wait.return_value = True

    env = {
        'SHPKPR_MARATHON_URL': "http://marathon.somedomain.com:8080",
        'SHPKPR_MARATHON_APP_ID': 'test-app',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
        'SHPKPR_LABEL_SOME_LABEL': 'somevalue',
    }
    result = runner(['apps', 'deploy'], env=env)

    assert result.exit_code == 0
