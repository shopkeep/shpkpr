import click
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


def _task_status(_app):
    """Check marathon app status
    """
    if len(_app.deployments) > 0:
        return click.style("DEPLOYING", fg='yellow')
    if _app.tasks_running == 0:
        return click.style("SUSPENDED", fg='blue')
    if _app.tasks_unhealthy > 0:
        return click.style("UNHEALTHY", fg='red')
    return click.style("HEALTHY", fg='green')


@click.command('show', short_help='Show application details.', context_settings=CONTEXT_SETTINGS)
@params.application
@pass_context
def cli(ctx, application):
    """Shows detailed information for a single application."""
    ctx.vlog('Showing application: %s', application)
    ctx.vlog('=====================%s', '=' * len(application))

    _app = ctx.marathon_client.get_app(application)

    # print default application info
    ctx.log("ID:           %s", _app.id.lstrip('/'))
    ctx.log("CPUs:         %s", _app.cpus)
    ctx.log("RAM:          %s", _app.mem)
    ctx.log("Instances:    %s", _app.instances)
    ctx.log("Docker Image: %s", _app.container.docker.image)
    ctx.log("Domain:       %s", _app.labels.get("DOMAIN"))
    ctx.log("Version:      %s", _app.version)
    ctx.log("Status:       %s", _task_status(_app))
