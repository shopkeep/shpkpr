# third-party import
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


@click.command('show', short_help='Show application details.', context_settings=CONTEXT_SETTINGS)
@params.application
@pass_context
def cli(ctx, application_id):
    """Shows detailed information for a single application.
    """
    application = ctx.marathon_client.get_application(application_id)
    _pretty_print(ctx, application)


def _pretty_print(ctx, application):
    """Pretty print application details to stdout
    """
    ctx.log("ID:           %s", application.id.lstrip('/'))
    ctx.log("CPUs:         %s", application.cpus)
    ctx.log("RAM:          %s", application.mem)
    ctx.log("Instances:    %s", application.instances)
    ctx.log("Docker Image: %s", application.container.docker.image)
    ctx.log("Version:      %s", application.version)
    ctx.log("Status:       %s", _task_status(application))


def _task_status(application):
    """Returns a nicely formatted string we can use to display application health on the CLI.
    """
    if len(application.deployments) > 0:
        return click.style("DEPLOYING", fg='yellow')
    if application.tasks_running == 0:
        return click.style("SUSPENDED", fg='blue')
    if application.tasks_unhealthy > 0:
        return click.style("UNHEALTHY", fg='red')
    return click.style("HEALTHY", fg='green')
