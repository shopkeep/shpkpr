# third-party imports
import marathon
import mock
import pytest

# local imports
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
@mock.patch('shpkpr.marathon.MarathonClient._block_deployment')
def test_deploy_application(mock_block_deployment, mock_update_app):
    application = marathon.models.app.MarathonApp(id="test-app")
    mock_update_app.return_value = {'deploymentId': '1234', 'version': '1'}
    client = MarathonClient("http://marathon.somedomain.com:8080")
    client.deploy_application(application)
    mock_update_app.assert_called_with(application.id, application)
    mock_block_deployment.assert_called_with(application.id, mock_update_app.return_value)


@mock.patch('marathon.MarathonClient.update_app')
@mock.patch('shpkpr.marathon.MarathonClient._block_deployment')
def test_deploy_application_non_blocking(mock_block_deployment, mock_update_app):
    application = marathon.models.app.MarathonApp(id="test-app")
    mock_update_app.return_value = {'deploymentId': '1234', 'version': '1'}
    client = MarathonClient("http://marathon.somedomain.com:8080")
    client.deploy_application(application, block=False)
    mock_update_app.assert_called_with(application.id, application)
    mock_block_deployment.assert_not_called()


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_block_deployment(mock_get_application):
    """ Test that _block_deployment spins until a deployment succeeds.
    """
    deployment = {'deploymentId': '1234', 'version': '2'}

    app_state_pending = marathon.models.app.MarathonApp(
        deployments=[{'id': deployment['deploymentId']}],
        version='1',
        tasks_unhealthy=0
    )

    app_state_success = marathon.models.app.MarathonApp(
        deployments=[],
        version='2',
        tasks_unhealthy=0
    )

    mock_get_application.side_effect = [app_state_pending, app_state_success]
    client = MarathonClient("http://marathon.somedomain.com:8080")
    client._block_deployment('test-app', deployment)
    assert mock_get_application.call_count == 2


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_block_deployment_with_failing_deploy(mock_get_application):
    """ Test that _block_deployment raises an exception when the deployment
    fails.
    """
    deployment = {'deploymentId': '1234', 'version': '2'}

    app_state_failure = marathon.models.app.MarathonApp(
        deployments=[],
        version='1',
        tasks_unhealthy=0
    )

    mock_get_application.return_value = app_state_failure

    client = MarathonClient("http://marathon.somedomian.com:8080")
    with pytest.raises(DeploymentFailed):
        client._block_deployment('test-app', deployment)


@mock.patch('shpkpr.marathon.MarathonClient.get_application')
def test_block_deployment_with_unhealthy_tasks(mock_get_application):
    """ Test that _block_deployment raises an exception when the app has
    unhealthy tasks following a deployment.
    """
    deployment = {'deploymentId': '1234', 'version': '2'}

    app_state_unhealthy = marathon.models.app.MarathonApp(
        deployments=[],
        version='2',
        tasks_unhealthy=1
    )

    mock_get_application.return_value = app_state_unhealthy

    client = MarathonClient("http://marathon.somedomian.com:8080")
    with pytest.raises(DeploymentFailed):
        client._block_deployment('test-app', deployment)
