# stdlib imports
import json

# third-party imports
import click

# local imports
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.group('cron', short_help='Manage Chronos Jobs', context_settings=CONTEXT_SETTINGS)
@pass_logger
def cli(logger):
    """Manage Chronos Jobs.
    """


@cli.command('show', short_help='List names all jobs in Chronos', context_settings=CONTEXT_SETTINGS)
@options.chronos_url
@options.job_name
@pass_logger
def show(logger, chronos_client, job_name):
    """List application configuration.
    """
    jobs = chronos_client.list()

    if job_name is None:
        logger.log(_pretty_print(jobs))
    else:
        logger.log(_pretty_print(filter(lambda j: job_name == j['name'], jobs)))


def _pretty_print(dict):
    """Pretty print a dict as a json structure
    """
    return json.dumps(dict, indent=4, sort_keys=True, separators=(',', ': '))
