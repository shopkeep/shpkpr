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

    def list_application_ids(self):
        """Returns ids of all applications currently deployed to marathon.
        """
        return sorted([app.id.lstrip('/') for app in self.client.list_apps()])

    def deploy_application(self, application, block=True):
        """Deploys the given application to Marathon.
        """
        _deployment = self.client.update_app(application.id, application)
        if block:
            self._block_deployment(application.id, _deployment)

    def _block_deployment(self, application_id, deployment, check_interval_secs=5):
        """Blocks execution until the given deployment has completed.

        If the deployment completes successfully this function will return None, if
        unsuccessful a `DeploymentFailed` exception is raised.
        """
        application = None
        _in_progress = True

        # check that the given deployment is not in progress
        while _in_progress:
            application = self.get_application(application_id)
            _in_progress = deployment['deploymentId'] in [x.id for x in application.deployments]
            if _in_progress:
                time.sleep(check_interval_secs)

        # check that the application's version is as we expect
        if not deployment['version'] == application.version:
            raise DeploymentFailed(deployment['deploymentId'])

        # check that the application's tasks are healthy (if appropriate)
        if application.tasks_unhealthy > 0:
            raise DeploymentFailed("Tasks Unhealthy: %d" % application.tasks_unhealthy)
