# third-party imports
import click

# local imports
from shpkpr import mesos
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger
from shpkpr.files import log_files


@click.command('logs', short_help='View/tail application logs.', context_settings=CONTEXT_SETTINGS)
@options.application_id
@options.stream
@options.lines
@options.completed
@options.follow
@options.mesos_client
@pass_logger
def cli(logger, mesos_client, follow, completed, lines, stream, application_id):
    """ Tail a file in a mesos task's sandbox.
    """

    # get tasks from mesos. We add a "." to the application ID to ensure that
    # we only get back tasks from the application we ask for. Mesos matching
    # for the fltr arg is greedy so this is necessary to restrict the output.
    tasks = mesos_client.get_tasks(application_id + ".", completed=completed)

    # If we couldn't find any running tasks for our app we tell the user.
    if not tasks:
        raise click.UsageError('No matching tasks. Exiting.')

    # for each of our found tasks, check the mesos sandbox of each one and get
    # a MesosFile object for each of the files we want to inspect.
    mesos_files = mesos._mesos_files(tasks, stream, mesos_client)
    if not mesos_files:
        raise click.UsageError('No matching files. Exiting.')

    log_files(logger, mesos_files, follow, lines)
