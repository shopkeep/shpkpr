# stdlib imports
import json
import os

# third-party imports
import mock
import pytest
import responses

# local imports
from shpkpr.marathon import ClientError
from shpkpr.marathon import DeploymentNotFound
from shpkpr.marathon import DryRun
from shpkpr.marathon import MarathonClient


def _load_json_fixture(name):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "fixtures", name + ".json")
    with open(path, 'r') as f:
        fixture = json.loads(f.read())
    return fixture


@responses.activate
def test_get_application():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=_load_json_fixture("valid_app"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    application = client.get_application('test-app')
    assert application['id'] == "/test-app"
    assert application['cmd'] is None


@responses.activate
def test_get_application_not_found():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=404,
                  json={"message": "App '/test-app' does not exist"})

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.get_application('test-app')


@responses.activate
def test_get_application_internal_server_error():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=500,
                  body="Internal Server Error")

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.get_application('test-app')


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deploy(mock_deployment_check):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=_load_json_fixture("deployment"))
    mock_deployment_check.return_value = True

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = client.deploy({"id": "test-app"})
    assert deployment.wait(check_interval_secs=0.1)


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deploy_multiple(mock_deployment_check):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/',
                  status=201,
                  json=_load_json_fixture("deployment"))
    mock_deployment_check.return_value = True

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = client.deploy([{"id": "test-app"}, {"id": "test-app-2"}])
    assert deployment.wait(check_interval_secs=0.1)


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deploy_single_app_list(mock_deployment_check):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=_load_json_fixture("deployment"))
    mock_deployment_check.return_value = True

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = client.deploy([{"id": "test-app"}])
    assert deployment.wait(check_interval_secs=0.1)


@responses.activate
def test_deploy_conflict():
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=409,
                  json=_load_json_fixture("deployment_in_progress"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.deploy({"id": "test-app"})


@responses.activate
def test_deploy_dry_run():
    client = MarathonClient("http://marathon.somedomain.com:8080", dry_run=True)
    with pytest.raises(DryRun):
        client.deploy({"id": "test-app"})


@responses.activate
def test_deploy_unprocessable_entity():
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=422,
                  json=_load_json_fixture("validation_errors"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.deploy({"id": "test-app"})


@responses.activate
def test_get_deployment():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/deployments',
                  status=200,
                  json=_load_json_fixture("deployments"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = client.get_deployment("97c136bf-5a28-4821-9d94-480d9fbb01c8")
    assert deployment is not None
    assert deployment['id'] == "97c136bf-5a28-4821-9d94-480d9fbb01c8"


@responses.activate
def test_get_deployment_not_found():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/deployments',
                  status=200,
                  json=_load_json_fixture("deployments"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(DeploymentNotFound):
        client.get_deployment("1234")


@responses.activate
def test_basic_auth_headers_present():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=_load_json_fixture("valid_app"))

    client = MarathonClient("http://marathon.somedomain.com:8080",
                            "some-username",
                            "some-password")
    client.get_application('test-app')

    assert "Authorization" in responses.calls[0].request.headers


@responses.activate
def test_basic_auth_headers_not_present():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=200,
                  json=_load_json_fixture("valid_app"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    client.get_application('test-app')

    assert "Authorization" not in responses.calls[0].request.headers
