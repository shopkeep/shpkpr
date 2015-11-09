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

    _list = ctx.marathon_client.list_apps()
    _list = [app.id.lstrip('/') for app in sorted(_list)]
    for app in _list:
        ctx.log(app)
