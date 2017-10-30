# stdlib imports
import logging
import time

# local imports
from .prepare import prepare_app_definition
from .validate import Validator
from .wait import SwapApplicationTimeout
from .wait import Waiter
from shpkpr.marathon import DeploymentFailed
from cached_property import cached_property

logger = logging.getLogger(__name__)


class BlueGreenDeployment(object):
    """BluegreenDeployment implements a blue-green deployment strategy for
    web-facing applications on Marathon.

    It builds on the primitives provided by Marathon to provide zero-downtime
    deployments for HTTP services exposed to the web via Marathon-LB.
    """

    def __init__(self, marathon_client, marathon_lb_client, timeout, app_definitions, **kw):
        self.marathon_client = marathon_client
        self.marathon_lb_client = marathon_lb_client
        self.timeout = timeout
        self.app_definitions = app_definitions

    def execute(self, force=False):
        """Execute a bluegreen deployment.

        The mechanics of a bluegreen deploy mean that we have to deploy each
        application in turn (instead of the all-at-once approach used for
        standard deployments).

        NOTE: We could maybe be smarter here in future e.g. perhaps don't tear
        down old stacks until _all_ new stacks are running so we can roll back
        partially successful invocations.
        """
        app_ids = ", ".join([a["id"] for a in self.app_definitions])
        logger.info("Executing bluegreen deployment: {0}".format(app_ids))

        for app_definition in self.app_definitions:
            self.execute_for_app(app_definition, force)

    def execute_for_app(self, app_definition, force):
        """Execute a bluegreen deployment for a single application.
        """
        deployment = BlueGreenDeploymentSingleApp(self.marathon_client,
                                                  self.marathon_lb_client,
                                                  self.timeout,
                                                  app_definition)
        return deployment.execute(force=force)


class BlueGreenDeploymentSingleApp(object):

    def __init__(self, marathon_client, marathon_lb_client, timeout, app_definition):
        self.marathon_client = marathon_client
        self.marathon_lb_client = marathon_lb_client
        self.timeout = timeout
        self.app_definition = app_definition

    def execute(self, force=False):
        """Execute a bluegreen deployment for a single application.
        """
        Validator(self.marathon_client).validate(self.app_definition)

        # prepare the new application for deployment by setting the appropriate
        # labels and transforming the app's ID as appropriate. These changes
        # will allow Marathon-LB to cut the traffic over to the new app once
        # deployed.
        apps_state = self._fetch_apps_state
        marathon_info = self._fetch_marathon_info
        old_app_definition = self._fetch_old_app_definition()
        new_app_definition = prepare_app_definition(self.app_definition, old_app_definition, apps_state, marathon_info)

        # deploy the new application, wait until the traffic is cut over and
        # then tear down the old stack. If the process fails for any reason then
        # we roll back by tearing down the newly deployed stack at which point
        # Marathon-LB will begin serving traffic to the old application again
        # (if it had already stopped).
        old_app_id = old_app_definition["id"] if old_app_definition else None
        new_app_id = new_app_definition["id"]
        try:
            self._deploy_new_application(new_app_definition)
            self._wait_for_traffic_swap(old_app_id, new_app_id)
        except (DeploymentFailed, SwapApplicationTimeout):
            self._remove_new_application(new_app_id)
        else:
            self._remove_old_application(old_app_id)

    def _deploy_new_application(self, new_app_definition):
        """Deploy a new application definition to Marathon.
        """
        deployment = self.marathon_client.deploy([new_app_definition])

        logger.info("Waiting for marathon deployment to complete: {0}".format(deployment.deployment_id))
        result = deployment.wait(timeout=self.timeout)
        logger.info("Marathon deployment complete: {0}".format(deployment.deployment_id))
        return result

    def _wait_for_traffic_swap(self, old_app_id, new_app_id):
        """Wait for traffic to cut over from the old to the new application
        """
        if old_app_id is None:
            return

        waiter = Waiter(self.marathon_client,
                        self.marathon_lb_client,
                        new_app_id,
                        old_app_id)

        deadline = time.time() + self.timeout
        return waiter.wait(deadline)

    def _remove_application(self, app_id):
        """Remove a deployed application from Marathon
        """
        success = self.marathon_client.delete_application(app_id)
        if success:
            logger.info("Successfully removed application: %s", app_id)
        else:
            logger.info("Unable to remove application, manual intervention required: %s", app_id)
        return success

    def _remove_new_application(self, app_id):
        """Removes the newly started application after a deploy error
        """
        logger.info("Deployment failed: removing newly deployed stack")
        self._remove_application(app_id)
        raise DeploymentFailed("Deployment failed")

    def _remove_old_application(self, app_id):
        """Removes the old application after a successful deploy
        """
        if app_id is None:
            return

        logger.info("About to delete old application: %s", app_id)
        if not self._remove_application(app_id):
            raise DeploymentFailed("Deployment failed")

    def _fetch_old_app_definition(self):
        """Fetches the application definition for the currently deployed stack
        from Marathon if one exists. If no existing stacks are found then
        ``None`` is returned instead.
        """
        def get_deployment_group(app_definition):
            labels = app_definition.get('labels', {})
            return labels.get('HAPROXY_DEPLOYMENT_GROUP')

        target_deployment_group = get_deployment_group(self.app_definition)
        for app_definition in self._fetch_apps_state:
            if get_deployment_group(app_definition) == target_deployment_group:
                return app_definition
        return None

    @cached_property
    def _fetch_marathon_info(self):
        """Fetch current marathon configuration info
        """
        return self.marathon_client.get_info()

    @cached_property
    def _fetch_apps_state(self):
        """Fetch current marathon app state
        """
        return self.marathon_client.list_applications()
