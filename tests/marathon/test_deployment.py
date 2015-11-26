# third-party imports
import mock
import pytest

# local imports
from shpkpr.marathon import DeploymentFailed
from shpkpr.marathon import MarathonApplication
from shpkpr.marathon import MarathonClient
from shpkpr.marathon import MarathonDeployment
from shpkpr.marathon import default_schema


@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deployment_wait(mock_deployment_check):
    """ Test that deployment.wait() spins until a deployment succeeds.
    """
    mock_deployment_check.side_effect = [False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, True]

    client = MarathonClient("http://marathon.somedomain.com:8080", default_schema())
    deployment = MarathonDeployment(client, "", '1234', '2')
    deployment.wait(check_interval_secs=0.01)
    assert mock_deployment_check.call_count == 20


@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deployment_wait_with_timeout(mock_deployment_check):
    """ Test that deployment.wait() spins until a deployment succeeds.
    """
    mock_deployment_check.side_effect = [False, False, False]

    client = MarathonClient("http://marathon.somedomain.com:8080", default_schema())
    deployment = MarathonDeployment(client, "", '1234', '2')
    with pytest.raises(DeploymentFailed):
        deployment.wait(timeout=1, check_interval_secs=0.5)
    assert mock_deployment_check.call_count == 3


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_deployment_check_with_deployment_in_progress(mock_get_application):
    """ Test that deployment.check() returns False when the app has a deployment in progress.
    """
    client = MarathonClient("http://marathon.somedomian.com:8080", default_schema())
    app_state_failure = MarathonApplication(client._parse_response('''{
        "deployments": [{"id": "1234"}],
        "version": "2",
        "tasks_unhealthy": 0
    }'''))
    mock_get_application.return_value = app_state_failure

    deployment = MarathonDeployment(client, "", '1234', '2')
    assert deployment.check() == False


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_deployment_check_with_failing_deploy(mock_get_application):
    """ Test that deployment.check() raises an exception when the app has the
    wrong version following a deployment.
    """
    client = MarathonClient("http://marathon.somedomian.com:8080", default_schema())
    app_state_failure = MarathonApplication(client._parse_response('''{
        "deployments": [],
        "version": "1",
        "tasks_unhealthy": 0
    }'''))
    mock_get_application.return_value = app_state_failure

    deployment = MarathonDeployment(client, "", '1234', '2')
    with pytest.raises(DeploymentFailed):
        deployment.check()


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_deployment_check_with_unhealthy_tasks(mock_get_application):
    """ Test that deployment.check() raises an exception when the app has
    unhealthy tasks following a deployment.
    """
    client = MarathonClient("http://marathon.somedomian.com:8080", default_schema())
    app_state_unhealthy = MarathonApplication(client._parse_response('''{
        "deployments": [],
        "version": "2",
        "tasks_unhealthy": 1
    }'''))
    mock_get_application.return_value = app_state_unhealthy

    deployment = MarathonDeployment(client, "", '1234', '2')
    with pytest.raises(DeploymentFailed):
        deployment.check()
