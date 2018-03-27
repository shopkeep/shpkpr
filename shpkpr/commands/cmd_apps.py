# stdlib imports
import logging
import sys

# third-party imports
import click
import docker

# local imports
from shpkpr.cli import arguments
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.deployment import BlueGreenDeployment
from shpkpr.deployment import StandardDeployment
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template
from shpkpr.vault import resolve_secrets


logger = logging.getLogger(__name__)


def _validate_strategy_bluegreen(marathon_lb_client, **kw):
    if marathon_lb_client is None:
        msg = 'Missing option "--marathon_lb_url".'
        raise click.UsageError(msg)


STRATEGIES = {
    "standard": {
        "executor": StandardDeployment,
        "validator": lambda **kw: None,
        "default_template": "marathon/default/standard.json.tmpl",
    },
    "bluegreen": {
        "executor": BlueGreenDeployment,
        "validator": _validate_strategy_bluegreen,
        "default_template": "marathon/default/bluegreen.json.tmpl",
    },
}


@click.group('apps', context_settings=CONTEXT_SETTINGS)
def cli():
    """Manage Marathon applications.
    """


@cli.command(short_help='Deploy an application to Marathon.',
             context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.force
@options.template_names
@options.template_path
@options.env_prefix
@options.timeout
@options.deployment_strategy
@options.marathon_lb_client
@options.marathon_client
def deploy(marathon_client, marathon_lb_client, deployment_strategy, timeout,
           env_prefix, template_path, template_names, force, env_pairs, **kw):
    """Deploy one or more applications to Marathon.
    """
    # select the appropriate deployment strategy
    strategy = STRATEGIES[deployment_strategy]

    # use the default template if none was specified
    if not template_names:
        template_names = [strategy["default_template"]]

    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    rendered_templates = []
    for template_name in template_names:
        rendered_templates.append(render_json_template(template_path, template_name, **values))

    # perform some extra pre-flight validation if required, and execute the
    # deployment, blocking until complete.
    deployment_params = {"marathon_client": marathon_client,
                         "marathon_lb_client": marathon_lb_client,
                         "timeout": timeout,
                         "app_definitions": rendered_templates}
    strategy["validator"](**deployment_params)
    strategy["executor"](**deployment_params).execute(force)


@cli.command(short_help='Show application details.',
             context_settings=CONTEXT_SETTINGS)
@options.output_formatter
@options.application_id
@options.marathon_client
def show(marathon_client, application_id, output_formatter, **kw):
    """Show detailed information for one or more applications.
    """
    if application_id is None:
        payload = marathon_client.list_applications()
    else:
        payload = marathon_client.get_application(application_id)
    logger.info(output_formatter.format(payload))


@cli.command(short_help='Run a one-off task in a production-like environment.',
             context_settings=CONTEXT_SETTINGS)
@arguments.command
@arguments.env_pairs
@options.vault_client
@options.template_names
@options.template_path
@options.env_prefix
def run(env_prefix, template_path, template_names, vault_client, command, env_pairs, **kw):
    """Run a one-off task in a "production-like" environment.

    Uses the current deployment configuration to start up a container locally
    and run a single command. Environment variables and secrets are extracted
    from the current deployment configuration and injected into the container
    when starting up.
    """
    # use the default template if none was specified. We can just use the
    # standard template here since all we care about are environment variables
    # and secrets.
    if not template_names:
        template_name = STRATEGIES["standard"]["default_template"]
    else:
        template_name = template_names[0]

    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    rendered_template = render_json_template(template_path, template_name, **values)

    # extract required configuration from the rendered template
    app_id = rendered_template["id"]
    docker_image = rendered_template["container"]["docker"]["image"]
    environment_variables = rendered_template["env"]
    environment_variables.update(resolve_secrets(vault_client, rendered_template))

    logger.info("Running command for app ({0}): {1}\n".format(app_id, command))

    docker_client = docker.from_env()
    container = docker_client.containers.run(docker_image,
                                             command,
                                             detach=True,
                                             auto_remove=True,
                                             environment=environment_variables)

    # stream logs from the running container to stdout
    for line in container.logs(stream=True):
        logger.info(line.decode('utf-8').rstrip())

    # exit with the container's exit code once it finishes
    sys.exit(container.wait()['StatusCode'])
