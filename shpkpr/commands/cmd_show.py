# third-party import
import click

# local imports
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.command('show', short_help='Show application details.', context_settings=CONTEXT_SETTINGS)
@options.output_formatter
@options.application_id
@options.marathon_client
@pass_logger
def cli(logger, marathon_client, application_id, output_formatter):
    """Shows detailed information for one or more applications.
    """
    if application_id is None:
        payload = marathon_client.list_applications()
    else:
        payload = marathon_client.get_application(application_id)
    logger.log(output_formatter.format(payload))
