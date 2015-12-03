# stdlib imports
import datetime
import time

# local imports
from shpkpr import exceptions


class DeploymentFailed(exceptions.ShpkprException):
    pass


class MarathonDeployment(object):
    """Marathon deployment object.

    Allows the caller to check a deployment's status and cancel or rollback a
    deployment.
    """

    def __init__(self, client, application_id, deployment_id, expected_version):
        self._client = client
        self._application_id = application_id
        self._deployment_id = deployment_id
        self._expected_version = expected_version

    def check(self):
        """Check if this deployment has completed.

        If the deployment is in progress, return False, if the deployment
        completes successfully return True. If the deployment fails for any
        reason then a DeploymentFailed exception is raised.
        """
        application = self._client.get_application(self._application_id)

        # if the deployment is in progress then return False
        if self._deployment_id in [x['id'] for x in application['deployments']]:
            return False

        # check that the application's version is as we expect
        if not self._expected_version == application['version']:
            raise DeploymentFailed("Version mismatch: %s != %s" % (self._expected_version, application['version']))

        # check that the application's tasks are healthy (if appropriate)
        if application['tasksUnhealthy'] > 0:
            raise DeploymentFailed("Tasks Unhealthy: %d" % application['tasksUnhealthy'])

        # if the application isn't deploying, has the right version and is
        # healthy, then we can consider the deployment as completed
        # successfully and return True
        return True

    def wait(self, timeout=900, check_interval_secs=5):
        """Waits for a deployment to finish

        If a deployment completes successfully, True is returned, if it fails
        for any reason a DeploymentFailed exception is raised. If the
        deployment does not complete within ``timeout`` seconds, a
        DeploymentFailed exception is raised.

        ``check_interval_secs`` is used to determine the delay between
        subsequent checks. The default of 5 seconds is adequate for normal
        use.
        """
        _started = datetime.datetime.utcnow()

        while True:

            time.sleep(check_interval_secs)

            # check if the deployment has completed, if it has we return True
            if self.check():
                return True

            # if the specified timeout has elapsed we raise a DeploymentFailed error
            delta = datetime.datetime.utcnow() - _started
            if delta.total_seconds() > timeout:
                raise DeploymentFailed('Timed out: %d seconds' % timeout)
