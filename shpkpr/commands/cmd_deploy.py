# stdlib imports
import json
import os

# third-party imports
import click
from jinja2 import Template
from marathon.exceptions import NotFoundError
from marathon.models import MarathonApp

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import DeploymentFailed
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


@click.command('deploy', short_help='Deploy application from template.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@click.option('-t',
              '--template',
              'template_file',
              type=click.File("r"),
              required=True,
              help="Path of the template to use for deployment.")
@pass_context
def cli(ctx, template_file, instances, mem, cpus, application_id):
    """Deploy application from template.
    """
    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=CONTEXT_SETTINGS['auto_envvar_prefix'])
    try:
        rendered_template = render_json_template(template_file, **values)
    except ValueError as e:
        raise click.ClickException("Invalid JSON: " + str(e))
    application = MarathonApp.from_json(rendered_template)

    # load existing config from marathon if available
    try:
        existing_application = ctx.marathon_client.get_application(application_id)
    except NotFoundError:
        existing_application = None

    # set instances value if specified
    if instances is not None:
        application.instances = instances
    # otherwise use the existing value from marathon
    elif existing_application is not None and not application.instances:
        application.instances = existing_application.instances
    # set a default value for instances if not specified
    if application.instances is None:
        application.instances = 1

    # set mem value if specified
    if mem is not None:
        application.mem = mem
    # otherwise use the existing value from marathon
    elif existing_application is not None and not application.mem:
        application.mem = existing_application.mem
    # set a default value for instances if not specified
    if application.mem is None:
        application.mem = 512

    # set cpus value if specified
    if cpus is not None:
        application.cpus = cpus
    # otherwise use the existing value from marathon
    elif existing_application is not None and not application.cpus:
        application.cpus = existing_application.cpus
    # set a default value for cpus if not specified
    if application.cpus is None:
        application.cpus = 0.1

    # set the application ID to the value specified on the command line (unconditionally)
    application.id = application_id

    deployment = ctx.marathon_client.deploy_application(application)
    try:
        deployment.wait()
    except DeploymentFailed as e:
        raise click.ClickException(str(e))
