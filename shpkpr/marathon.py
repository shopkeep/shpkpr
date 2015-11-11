"""A collection of marathon-related utils
"""
# future imports
from __future__ import absolute_import

# stdlib imports
import time

# third-party imports
from marathon import MarathonClient as MaraClient


class DeploymentFailed(Exception):
    pass


class MarathonClient(object):
    """A thin wrapper around marathon.MarathonClient for internal use
    """

    def __init__(self, marathon_url):
        self.client = MaraClient(marathon_url)

    def get_application(self, application_id):
        """Returns detailed information for a single application.
        """
        return self.client.get_app(application_id)

    def list_applications(self):
        """Returns ids of all applications currently deployed to marathon.
        """
        return [app.id.lstrip('/') for app in sorted(self.client.list_apps())]

    def deploy_application(self, application, block=True):
        """Deploys the given application to Marathon.
        """
        _deployment = self.client.update_app(application.id, application)
        if block:
            self._block_deployment(application.id, _deployment)

    def _block_deployment(self, application_id, deployment):
        """Blocks execution until the given deployment has completed.

        If the deployment completes successfully this function will return None, if
        unsuccessful a `DeploymentFailed` exception is raised.
        """
        _app = None
        _in_progress = True

        # check that the given deployment is not in progress
        while _in_progress:
            _app = self.get_application(application_id)
            _in_progress = deployment['deploymentId'] in [x.id for x in _app.deployments]
            if _in_progress:
                time.sleep(5)

        # check that the application's version is as we expect
        if not deployment['version'] == _app.version:
            raise DeploymentFailed(deployment['deploymentId'])

        # check that the application's tasks are healthy (if appropriate)
        if _app.tasks_unhealthy > 0:
            raise DeploymentFailed("Tasks Unhealthy: %d" % _app.tasks_unhealthy)
