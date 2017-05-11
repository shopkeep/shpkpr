# stdlib imports
import json
import logging
import time

# third-party imports
import click

# local imports
from shpkpr import exceptions
from shpkpr.marathon import DeploymentFailed
from shpkpr.bluegreen import SwapApplicationTimeout
from shpkpr.bluegreen import fetch_previous_deploys
from shpkpr.bluegreen import prepare_deploy
from shpkpr.bluegreen import select_last_deploy
from shpkpr.bluegreen import swap_bluegreen_apps
from shpkpr.bluegreen import validate_app


logger = logging.getLogger(__name__)


class DualStackAlreadyExists(exceptions.ShpkprException):
    """Raised if a deploy is attempt whilst both a blue and green stack
    already exist in Marathon
    """
    exit_code = 2

    def format_message(self):
        msg = "Both blue and green stacks detected on Marathon, please resolve "
        msg += "before deploying. This may mean that another deploy is in progress."
        return msg


class BlueGreenDeployment(object):
    """BluegreenDeployment implements a blue-green deployment strategy for
    web-facing applications on Marathon. It builds on the primitives provided by
    Marathon to provide zero-downtime deployments for HTTP services exposed to
    the web via Marathon-LB.
    """

    def __init__(self, marathon_client, marathon_lb_client, max_wait, app_definitions):
        self.marathon_client = marathon_client
        self.marathon_lb_client = marathon_lb_client
        self.max_wait = max_wait
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
        for app in self.app_definitions:
            validate_app(app)

            # fetch all previous deploys from marathon and abort if there is more
            # than one stack currently active.
            previous_deploys = fetch_previous_deploys(self.marathon_client, app)
            if len(previous_deploys) > 1:
                raise DualStackAlreadyExists("Both blue and green apps detected")
            # transform the app to be deployed to apply the correct labels and
            # ID-change that will allow marathon-lb to cut traffic over as necessary.
            new_app = prepare_deploy(previous_deploys, app)

            logger.info('Final App Definition:')
            logger.info(json.dumps(new_app, indent=4, sort_keys=True))
            if force or click.confirm("Continue with deployment?"):
                try:
                    self.deploy_and_swap(new_app, previous_deploys, force)
                except (DeploymentFailed, SwapApplicationTimeout):
                    self.remove_new_stack(app['id'], force)

    def deploy_and_swap(self, new_app, previous_deploys, force):
        """Deploy a new application and swap traffic from the old one once complete.
        """
        self.marathon_client.deploy([new_app]).wait(timeout=self.max_wait)

        if len(previous_deploys) == 0:
            # This was the first deploy, nothing to swap
            return True
        else:
            # This is a standard blue/green deploy, swap new app with old
            old_app = select_last_deploy(previous_deploys)
            return swap_bluegreen_apps(force,
                                       self.max_wait,
                                       self.marathon_client,
                                       self.marathon_lb_client,
                                       new_app,
                                       old_app,
                                       time.time())

    def remove_new_stack(self, app_id, force):
        """Removes the newly started stack after a deploy error
        """
        logger.info("Deployment failed: removing newly deployed stack")
        success = self.marathon_client.delete_application(app_id, force=force)
        if success:
            logger.info("Successfully removed newly deployed stack: %s", app_id)
        else:
            logger.info("Unable to remove newly deployed stack, manual intervention required: %s", app_id)
        raise DeploymentFailed("Deployment failed")
