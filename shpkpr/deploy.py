# stdlib import
import time


class DeploymentFailed(Exception):
    pass


def block_deployment(client, app_id, deployment):
    """Blocks execution until the given deployment has completed.

    If the deployment completes successfully this function will return None, if
    unsuccessful a `DeploymentFailed` exception is raised.
    """
    _app = None
    _in_progress = True

    # check that the given deployment is not in progress
    while _in_progress:
        _app = client.get_app(app_id)
        _in_progress = deployment['deploymentId'] in [x.id for x in _app.deployments]
        if _in_progress:
            time.sleep(5)

    # check that the application's version is as we expect
    if not deployment['version'] == _app.version:
        raise DeploymentFailed(deployment['deploymentId'])

    # check that the application's tasks are healthy (if appropriate)
    if _app.tasks_unhealthy > 0:
        raise DeploymentFailed("Tasks Unhealthy: %d" % _app.tasks_unhealthy)
