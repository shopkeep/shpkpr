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


@cli.command('test', short_help='Test Command', context_settings=CONTEXT_SETTINGS)
@options.chronos_url
@pass_logger
def list(logger, chronos_url):
    """List application configuration.
    """
    logger.log(chronos_url)
