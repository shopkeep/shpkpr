# stdlib imports
import json
import os

# third-party imports
import mock
import pytest
import responses

# local imports
from shpkpr.marathon import ClientError
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
def test_list_application_ids():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps',
                  status=200,
                  json=_load_json_fixture("valid_apps"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    application_ids = client.list_application_ids()
    assert application_ids == ['test-app-a', 'test-app-b', 'test-app-c']


@responses.activate
def test_list_application_ids_internal_server_error():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps',
                  status=500,
                  body="Internal Server Error")

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.list_application_ids()


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deploy_application(mock_deployment_check):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=201,
                  json=_load_json_fixture("deployment"))
    mock_deployment_check.return_value = True

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = client.deploy_application({"id": "test-app"})
    assert deployment.wait() == True


@responses.activate
def test_deploy_application_conflict():
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=409,
                  json=_load_json_fixture("deployment_in_progress"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.deploy_application({"id": "test-app"})


@responses.activate
def test_deploy_application_unprocessable_entity():
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps/test-app',
                  status=422,
                  json=_load_json_fixture("validation_errors"))

    client = MarathonClient("http://marathon.somedomain.com:8080")
    with pytest.raises(ClientError):
        client.deploy_application({"id": "test-app"})
