"""Option parameter definitions for shpkpr.

All option parameters should be defined in this module, commands should not
define their options directly, instead all options should be defined here and
imported as required. This helps maintain consistency where a single option is
used for multiple commands.
"""
# third-party imports
import click

# local imports
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.marathon import MarathonClient
from shpkpr.mesos import MesosClient


application_id = click.option(
    '-a', '--application',
    'application_id',
    envvar="{0}_APPLICATION".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help="ID/name of the application to scale.",
)


completed = click.option(
    '-c', '--completed',
    is_flag=True,
    help='Show logs for completed tasks.',
)


cpus = click.option(
    '-c', '--cpus',
    type=float,
    help="Number of CPUs to assign to each instance of the application.",
)


env_prefix = click.option(
    '-e', '--env_prefix',
    'env_prefix',
    default=CONTEXT_SETTINGS['auto_envvar_prefix'],
    help="Prefix used to restrict environment vars used for templating.",
)


follow = click.option(
    '-f', '--follow',
    is_flag=True,
    help='Enables follow mode.',
)


force = click.option(
    '--force',
    is_flag=True,
    help='Force update even if a deployment is in progress.',
)


instances = click.option(
    '-i', '--instances',
    type=int,
    help="Number of instances of the application to run.",
)


lines = click.option(
    '-n', '--lines',
    type=int,
    help='Number of lines to show in tail output.',
    default=10,
)


marathon_client = click.option(
    '--marathon_url',
    'marathon_client',
    envvar="{0}_MARATHON_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help="URL of the Marathon API to use.",
    callback=lambda c, p, v: MarathonClient(v)
)


mem = click.option(
    '-m', '--mem',
    type=int,
    help="Amount of RAM (in MB) to assign to each instance of the application.",
)


mesos_client = click.option(
    '--mesos_master_url',
    'mesos_client',
    envvar="{0}_MESOS_MASTER_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help="URL of the Mesos master to use.",
    callback=lambda c, p, v: MesosClient(v)
)


stream = click.option(
    '--file',
    'stream',
    envvar="{0}_FILE".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    help='Which sandbox file to read from.',
    default="stdout",
)


template_file = click.option(
    '-t', '--template',
    'template_file',
    envvar="{0}_TEMPLATE".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    type=click.File("r"),
    required=True,
    help="Path of the template to use for deployment.",
)
