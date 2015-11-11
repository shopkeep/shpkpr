# third-party import
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


@click.command('show', short_help='Show application details.', context_settings=CONTEXT_SETTINGS)
@params.application
@pass_context
def cli(ctx, application):
    """Shows detailed information for a single application."""
    ctx.vlog('Showing application: %s', application)
    ctx.vlog('=====================%s', '=' * len(application))

    _app = ctx.marathon_client.get_application(application)
    _format_output(_app)


def _format_output(ctx, application):
    """Pretty print application details to stdout
    """
    ctx.log("ID:           %s", application.id.lstrip('/'))
    ctx.log("CPUs:         %s", application.cpus)
    ctx.log("RAM:          %s", application.mem)
    ctx.log("Instances:    %s", application.instances)
    ctx.log("Docker Image: %s", application.container.docker.image)
    ctx.log("Domain:       %s", application.labels.get("DOMAIN"))
    ctx.log("Version:      %s", application.version)
    ctx.log("Status:       %s", _task_status(application))


def _task_status(_app):
    """Returns a nicely formatted string we can use to display application health on the CLI.
    """
    if len(_app.deployments) > 0:
        return click.style("DEPLOYING", fg='yellow')
    if _app.tasks_running == 0:
        return click.style("SUSPENDED", fg='blue')
    if _app.tasks_unhealthy > 0:
        return click.style("UNHEALTHY", fg='red')
    return click.style("HEALTHY", fg='green')
