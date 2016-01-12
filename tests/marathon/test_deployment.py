# third-party imports
import mock
import pytest

# local imports
from shpkpr.marathon import DeploymentFailed
from shpkpr.marathon import DeploymentNotFound
from shpkpr.marathon import MarathonClient
from shpkpr.marathon import MarathonDeployment


@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deployment_wait(mock_deployment_check):
    """ Test that deployment.wait() spins until a deployment succeeds.
    """
    mock_deployment_check.side_effect = [False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, True]

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = MarathonDeployment(client, '1234')
    deployment.wait(check_interval_secs=0.01)
    assert mock_deployment_check.call_count == 20


@mock.patch('shpkpr.marathon.MarathonDeployment.check')
def test_deployment_wait_with_timeout(mock_deployment_check):
    """ Test that deployment.wait() spins until a deployment succeeds.
    """
    mock_deployment_check.side_effect = [False, False, False]

    client = MarathonClient("http://marathon.somedomain.com:8080")
    deployment = MarathonDeployment(client, '1234')
    with pytest.raises(DeploymentFailed):
        deployment.wait(timeout=1, check_interval_secs=0.5)
    assert mock_deployment_check.call_count == 2


@mock.patch('shpkpr.marathon.MarathonClient.get_deployment')
def test_deployment_check(mock_get_deployment):
    """ Test that deployment.check() returns True when the app has deployed successfully.
    """
    mock_get_deployment.side_effect = DeploymentNotFound("1234")

    client = MarathonClient("http://marathon.somedomian.com:8080")
    deployment = MarathonDeployment(client, '1234')
    assert deployment.check()


@mock.patch('shpkpr.marathon.MarathonClient.get_deployment')
def test_deployment_check_with_deployment_in_progress(mock_get_deployment):
    """ Test that deployment.check() returns False when the app has a deployment in progress.
    """
    deploy_in_progress = {
        "id": "97c136bf-5a28-4821-9d94-480d9fbb01c8",
        "version": "2015-09-30T09:09:17.614Z",
        "affectedApps": ["/foo"],
        "steps": [
            [
                {
                    "action": "StartApplication",
                    "app": "/foo"
                }
            ],
            [
                {
                    "action": "ScaleApplication",
                    "app": "/foo"
                }
            ]
        ],
        "currentActions": [
            {
                "action": "ScaleApplication",
                "app": "/foo"
            }
        ],
        "currentStep": 2,
        "totalSteps": 2
    }
    mock_get_deployment.return_value = deploy_in_progress

    client = MarathonClient("http://marathon.somedomian.com:8080")
    deployment = MarathonDeployment(client, "97c136bf-5a28-4821-9d94-480d9fbb01c8")
    assert not deployment.check()
