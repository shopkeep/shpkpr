# third-party imports
import click

# local imports
from shpkpr.cli import arguments
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


@click.command('deploy', short_help='Deploy application from template.', context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.force
@options.template_name
@options.template_path
@options.env_prefix
@options.marathon_client
@pass_logger
def cli(logger, marathon_client, env_prefix, template_path, template_name, force, env_pairs):
    """Deploy application from template.
    """
    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    rendered_template = render_json_template(template_path, template_name, **values)

    marathon_client.deploy_application(rendered_template, force=force).wait()
