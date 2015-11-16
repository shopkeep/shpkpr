# third-party imports
import marathon
import mock
import pytest

# local imports
from shpkpr.marathon import Deployment
from shpkpr.marathon import DeploymentFailed
from shpkpr.marathon import MarathonClient


@mock.patch('marathon.MarathonClient.get_app')
def test_get_application(mock_get_app):
    mock_get_app.return_value = marathon.models.app.MarathonApp(id='test-app')
    client = MarathonClient("http://marathon.somedomain.com:8080")
    application = client.get_application('test-app')
    assert application == mock_get_app.return_value


@mock.patch('marathon.MarathonClient.list_apps')
def test_list_application_ids(mock_list_apps):
    mock_list_apps.return_value = [
        marathon.models.app.MarathonApp(id='/app_c'),
        marathon.models.app.MarathonApp(id='/app_a'),
        marathon.models.app.MarathonApp(id='/app_b'),
    ]
    client = MarathonClient("http://marathon.somedomain.com:8080")
    application_ids = client.list_application_ids()
    assert application_ids == ['app_a', 'app_b', 'app_c']


@mock.patch('marathon.MarathonClient.update_app')
@mock.patch('shpkpr.marathon.Deployment.check')
def test_deploy_application(mock_deployment_check, mock_update_app):
    application = marathon.models.app.MarathonApp(id="test-app")
    mock_update_app.return_value = {'deploymentId': '1234', 'version': '1'}
    mock_deployment_check.return_value = True

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = client.deploy_application(application)
    mock_update_app.assert_called_with(application.id, application)
    assert deployment.wait() == True


@mock.patch('shpkpr.marathon.Deployment.check')
def test_deployment_wait(mock_deployment_check):
    """ Test that deployment.wait() spins until a deployment succeeds.
    """
    mock_deployment_check.side_effect = [False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, True]

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = Deployment(client, "", '1234', '2')
    deployment.wait(check_interval_secs=0.01)
    assert mock_deployment_check.call_count == 20


@mock.patch('shpkpr.marathon.Deployment.check')
def test_deployment_wait_with_timeout(mock_deployment_check):
    """ Test that deployment.wait() spins until a deployment succeeds.
    """
    mock_deployment_check.side_effect = [False, False, False]

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = Deployment(client, "", '1234', '2')
    with pytest.raises(DeploymentFailed):
        deployment.wait(timeout=1, check_interval_secs=0.5)
    assert mock_deployment_check.call_count == 3


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_deployment_check_with_failing_deploy(mock_get_application):
    """ Test that deployment.check() raises an exception when the app has the
    wrong version following a deployment.
    """
    app_state_failure = marathon.models.app.MarathonApp(
        deployments=[],
        version='1',
        tasks_unhealthy=0
    )
    mock_get_application.return_value = app_state_failure

    client = MarathonClient("http://marathon.somedomian.com:8080")
    deployment = Deployment(client, "", '1234', '2')
    with pytest.raises(DeploymentFailed):
        deployment.check()


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_deployment_check_with_unhealthy_tasks(mock_get_application):
    """ Test that deployment.check() raises an exception when the app has
    unhealthy tasks following a deployment.
    """
    app_state_unhealthy = marathon.models.app.MarathonApp(
        deployments=[],
        version='2',
        tasks_unhealthy=1
    )
    mock_get_application.return_value = app_state_unhealthy

    client = MarathonClient("http://marathon.somedomian.com:8080")
    deployment = Deployment(client, "", '1234', '2')
    with pytest.raises(DeploymentFailed):
        deployment.check()
