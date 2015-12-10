# third-party imports
import click

# local imports
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.command('list', short_help="Lists all deployed applications", context_settings=CONTEXT_SETTINGS)
@options.marathon_client
@pass_logger
def cli(logger, marathon_client):
    """Lists all applications currently deployed to marathon.
    """
    for application_id in marathon_client.list_application_ids():
        logger.log(application_id)
