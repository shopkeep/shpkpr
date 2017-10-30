# stdlib imports
import datetime
import time

# local imports
from shpkpr import exceptions


class DeploymentFailed(exceptions.ShpkprException):
    pass


class DeploymentNotFound(exceptions.ShpkprException):
    pass


class MarathonDeployment(object):
    """Marathon deployment object.

    Allows the caller to check a deployment's status and cancel or rollback a
    deployment.
    """

    def __init__(self, client, deployment_id):
        self._client = client
        self.deployment_id = deployment_id

    def check(self):
        """Check if this deployment has completed.

        This method returns a True when a deployment is complete, False when a
        deployment is in progress.
        """
        try:
            self._client.get_deployment(self.deployment_id)
        except DeploymentNotFound:
            # if the deployment isn't listed, then we can consider the deployment as completed
            # successfully and return True. According to the marathon docs: "If the deployment
            # is gone from the list of deployments, then this means it is finished."
            return True

        return False

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
