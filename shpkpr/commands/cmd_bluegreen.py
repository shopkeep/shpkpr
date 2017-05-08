# third-party imports
import click

# local imports
from shpkpr.cli import arguments
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.deployment import BlueGreenDeployment
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


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
def cli(marathon_client, marathon_lb_url, max_wait, force, env_prefix,
        template_path, template_names, env_pairs):
    """Perform a blue/green deploy
    """
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)

    rendered_templates = []
    for template_name in template_names:
        rendered_templates.append(render_json_template(template_path, template_name, **values))

    deployment = BlueGreenDeployment(marathon_client,
                                     marathon_lb_url,
                                     max_wait,
                                     rendered_templates)
    deployment.execute(force)
