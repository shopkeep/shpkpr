# third-party imports
import click
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
@click.option('-t',
              '--template',
              'template_file',
              type=click.File("r"),
              required=True,
              help="Path of the template to use for deployment.")
@click.option('-e',
              '--env_prefix',
              'env_prefix',
              default=CONTEXT_SETTINGS['auto_envvar_prefix'],
              help="Prefix used to restrict environment vars used for templating.")
@pass_context
def cli(ctx, env_prefix, template_file, application_id):
    """Deploy application from template.
    """
    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=env_prefix)
    rendered_template = render_json_template(template_file, **values)
    application = MarathonApp.from_json(rendered_template)

    # set the application ID to the value specified on the command line (if
    # not already set, as marathon requires this)
    if not application.id:
        application.id = application_id

    deployment = ctx.marathon_client.deploy_application(application)
    try:
        deployment.wait()
    except DeploymentFailed as e:
        raise click.ClickException(str(e))
