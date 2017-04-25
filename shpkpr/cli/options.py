"""Option parameter definitions for shpkpr.

All option parameters should be defined in this module, commands should not
define their options directly, instead all options should be defined here and
imported as required. This helps maintain consistency where a single option is
used for multiple commands.
"""
# stdlib imports
import os

# third-party imports
import click

# local imports
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.formatter import OutputFormatter
from shpkpr.marathon import MarathonClient


application_id = click.option(
    '-a', '--application',
    'application_id',
    envvar="{0}_APPLICATION".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    help="ID/name of the application to scale.",
)


dry_run = click.option(
    '--dry-run',
    is_flag=True,
    help='Enables dry-run mode. Shpkpr will not attempt to contact Marathon when this is enabled.',
)


env_prefix = click.option(
    '-e', '--env_prefix',
    'env_prefix',
    default=CONTEXT_SETTINGS['auto_envvar_prefix'],
    help="Prefix used to restrict environment vars used for templating.",
)


force = click.option(
    '--force',
    is_flag=True,
    help='Force update even if a deployment is in progress.',
)


marathon_client = click.option(
    '--marathon_url',
    'marathon_client',
    envvar="{0}_MARATHON_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help="URL of the Marathon API to use.",
    callback=lambda c, p, v: MarathonClient(v)
)


template_path = click.option(
    '--template_dir',
    'template_path',
    envvar="{0}_TEMPLATE_DIR".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    type=str,
    default=os.getcwd(),
    help="Base directory in which your templates are stored.",
)


template_names = click.option(
    '-t', '--template',
    'template_names',
    envvar="{0}_TEMPLATES".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    type=str,
    required=True,
    help="Path of the template to use for deployment.",
    multiple=True,
)

chronos_url = click.option(
    '--chronos_url',
    'chronos_url',
    envvar="{0}_CHRONOS_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help='URL of the Chronos endpoint to use'
)

chronos_version = click.option(
    '--chronos_version',
    'chronos_version',
    envvar="{0}_CHRONOS_VERSION".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=False,
    help='Verson of the Chronos endpoint to use',
    default='3.0.2'
)

job_name = click.option(
    '-j', '--job-name',
    type=str,
    help='Restrict command to specific job.',
)


marathon_lb_url = click.option(
    '--marathon_lb_url',
    'marathon_lb_url',
    envvar="{0}_MARATHON_LB_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help="url of marathon lb",
)


max_wait = click.option(
    '--max-wait',
    'max_wait',
    type=int,
    help='Maximum amount of time to wait for deployment to finish before aborting.',
    envvar="{0}_MAX_WAIT".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default=300,
)

output_formatter = click.option(
    '--output-format',
    'output_formatter',
    type=click.Choice(["json", "yaml"]),
    help='Serialization format to use when printing config data to stdout.',
    envvar="{0}_OUTPUT_FORMAT".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default="json",
    callback=lambda c, p, v: OutputFormatter(v)
)
