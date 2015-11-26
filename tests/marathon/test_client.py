# stdlib imports
import json
import os

# third-party imports
import mock
import responses

# local imports
from shpkpr.marathon import MarathonApplication
from shpkpr.marathon import MarathonClient
from shpkpr.marathon import default_schema


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

    client = MarathonClient("http://marathon.somedomain.com:8080", default_schema())
    application = client.get_application('test-app')
    assert application.id == "/test-app"
    assert len(application.tasks) == 2
    assert application.tasks[1].host == '10.210.51.111'
    application.tasks[1].host = '10.210.51'
    assert application.tasks[1].host == '10.210.51'
    assert application.env.IM_AN_ENV_VAR == "AND_IM_A_VALUE"
    assert application.container.docker.image == "my-docker-registry.com/test_app:master-be96e6"
    application.container.docker.image = "my-docker-registry.com/test_app:latest"
    assert application.container.docker.image == "my-docker-registry.com/test_app:latest"


@responses.activate
def test_list_application_ids():
    responses.add(responses.GET,
                  'http://marathon.somedomain.com:8080/v2/apps',
                  status=200,
                  json=_load_json_fixture("valid_apps"))

    client = MarathonClient("http://marathon.somedomain.com:8080", default_schema())
    application_ids = client.list_application_ids()
    assert application_ids == ['test-app-a', 'test-app-b', 'test-app-c']


@responses.activate
@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deploy_application(mock_deployment_check):
    responses.add(responses.PUT,
                  'http://marathon.somedomain.com:8080/v2/apps',
                  status=200,
                  json=_load_json_fixture("deployment"))
    mock_deployment_check.return_value = True

    client = MarathonClient("http://marathon.somedomain.com:8080", default_schema())
    application = MarathonApplication(client._parse_response('{"id": "test-app"}'), client.application_schema)
    deployment = client.deploy_application(application)
    assert deployment.wait() == True
