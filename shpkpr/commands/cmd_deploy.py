# third-party imports
import click

# local imports
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import MarathonApplication
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


@click.command('deploy', short_help='Deploy application from template.', context_settings=CONTEXT_SETTINGS)
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
              help="Path of the template to use for deployment.")
@pass_context
def cli(ctx, env_prefix, template_file):
    """Deploy application from template.
    """
    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=env_prefix)
    rendered_template = render_json_template(template_file, **values)

    application = MarathonApplication(rendered_template)
    ctx.marathon_client.deploy_application(application).wait()
