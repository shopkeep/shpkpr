# stdlib imports
import json

# third-party imports
import click
import time

# local imports
from shpkpr import exceptions
from shpkpr.cli import arguments
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template
from shpkpr.marathon import DeploymentFailed
from shpkpr.marathon_lb import SwapApplicationTimeout
from shpkpr.marathon_lb import fetch_previous_deploys
from shpkpr.marathon_lb import prepare_deploy
from shpkpr.marathon_lb import select_last_deploy
from shpkpr.marathon_lb import swap_bluegreen_apps
from shpkpr.marathon_lb import validate_app


class DualStackAlreadyExists(exceptions.ShpkprException):
    """Raised if a deploy is attempt whilst both a blue and green stack
    already exist in Marathon
    """
    exit_code = 2

    def format_message(self):
        msg = "Both blue and green stacks detected on Marathon, please resolve "
        msg += "before deploying. This may mean that another deploy is in progress."
        return msg


@click.command('bluegreen', short_help='perform a blue-green deploy of the application',
               context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.template_names
@options.template_path
@options.env_prefix
@options.marathon_client
@options.marathon_lb_url
@options.max_wait
@options.force
@pass_logger
def cli(logger, marathon_client, marathon_lb_url, max_wait, force, env_prefix,
        template_path, template_names, env_pairs):
    """Perform a blue/green deploy
    """
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)

    rendered_templates = []
    for template_name in template_names:
        rendered_templates.append(render_json_template(template_path, template_name, **values))

    for app in rendered_templates:
        validate_app(app)

        # fetch all previous deploys from marathon and abort if there is more
        # than one stack currently active.
        previous_deploys = fetch_previous_deploys(marathon_client, app)
        if len(previous_deploys) > 1:
            raise DualStackAlreadyExists("Both blue and green apps detected")
        # transform the app to be deployed to apply the correct labels and
        # ID-change that will allow marathon-lb to cut traffic over as necessary.
        new_app = prepare_deploy(previous_deploys, app)

        logger.log('Final App Definition:')
        logger.log(json.dumps(new_app, indent=4, sort_keys=True))
        if force or click.confirm("Continue with deployment?"):
            try:
                deploy_and_swap(marathon_client,
                                new_app,
                                previous_deploys,
                                logger,
                                force,
                                max_wait,
                                marathon_lb_url)
            except (DeploymentFailed, SwapApplicationTimeout):
                remove_new_stack(marathon_client, logger, app['id'], force)


def deploy_and_swap(marathon_client, new_app, previous_deploys, logger, force,
                    max_wait, marathon_lb_url):
    """Deploy a new application and swap traffic from the old one once complete.
    """
    marathon_client.deploy([new_app]).wait(timeout=max_wait)

    if len(previous_deploys) == 0:
        # This was the first deploy, nothing to swap
        return True
    else:
        # This is a standard blue/green deploy, swap new app with old
        old_app = select_last_deploy(previous_deploys)
        return swap_bluegreen_apps(logger,
                                   force,
                                   max_wait,
                                   marathon_client,
                                   marathon_lb_url,
                                   new_app,
                                   old_app,
                                   time.time())


def remove_new_stack(marathon_client, logger, app_id, force):
    """Removes the newly started stack after a deploy error
    """
    logger.log("Deployment failed: removing newly deployed stack")
    success = marathon_client.delete_application(app_id, force=force)
    if success:
        logger.log("Successfully removed newly deployed stack: %s", app_id)
    else:
        logger.log("Unable to remove newly deployed stack, manual intervention required: %s", app_id)
    raise DeploymentFailed("Deployment failed")
