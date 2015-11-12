# third-party imports
import click
from dcoscli import log

# local imports
from shpkpr import mesos
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


@click.command('logs', short_help='View/tail application logs.', context_settings=CONTEXT_SETTINGS)
@params.application
@click.option('--file', '_file', help='Which sandbox file to read from.', default="stdout")
@click.option('-n', '--lines', type=int, help='Number of lines to show in tail output.', default=10)
@click.option('-c', '--completed', is_flag=True, help='Show logs for completed tasks.')
@click.option('-f', '--follow', is_flag=True, help='Enables follow mode.')
@pass_context
def cli(ctx, follow, completed, lines, _file, application_id):
    """ Tail a file in a mesos task's sandbox.
    """

    # get tasks from mesos
    tasks = ctx.mesos_client.get_tasks(application_id, completed=completed)

    # If we couldn't find any running tasks for our app we tell the user.
    if not tasks:
        raise click.UsageError('No matching tasks. Exiting.')

    # for each of our found tasks, check the mesos sandbox of each one and get
    # a MesosFile object for each of the files we want to inspect.
    mesos_files = mesos._mesos_files(tasks, _file, ctx.mesos_client)
    if not mesos_files:
        raise click.UsageError('No matching tasks. Exiting.')

    # For now we're using dcoscli's logging functionality, but this should be
    # ported to use click.echo so that we have more control over formatting
    # and timing of the outputted logs.
    log.log_files(mesos_files, follow, lines)
