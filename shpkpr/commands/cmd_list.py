# third-party imports
import click

# local imports
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


@click.command('list', short_help="Lists all deployed applications", context_settings=CONTEXT_SETTINGS)
@pass_context
def cli(ctx):
    """Lists all applications currently deployed to marathon."""
    ctx.vlog('Listing deployed applications')
    ctx.vlog('=============================\n')

    for app in ctx.marathon_client.list_applications():
        ctx.log(app)
