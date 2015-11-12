# third-party imports
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import MarathonClient


@click.command('list', short_help="Lists all deployed applications", context_settings=CONTEXT_SETTINGS)
@params.marathon_url
@pass_context
def cli(ctx, marathon_url):
    """Lists all applications currently deployed to marathon.
    """
    for application_id in MarathonClient(marathon_url).list_application_ids():
        ctx.log(application_id)
