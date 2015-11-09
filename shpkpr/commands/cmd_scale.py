import click
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.deploy import block_deployment


@click.command('scale', short_help='Scale application resources.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@pass_context
def cli(ctx, instances, mem, cpus, application):
    """Scale application resources to specified levels."""
    _app = ctx.marathon_client.get_app(application)
    _updated = False

    if instances is not None and not _app.instances == instances:
        _updated = True
        _app.instances = instances
    if mem is not None and not _app.mem == mem:
        _updated = True
        _app.mem = mem
    if cpus is not None and not _app.cpus == cpus:
        _updated = True
        _app.cpus = cpus

    if _updated:
        ctx.vlog('Scaling application: %s', application)
        ctx.vlog('=====================%s', '=' * len(application))
        _deployment = ctx.marathon_client.update_app(application, _app)
        block_deployment(ctx.marathon_client, application, _deployment)
