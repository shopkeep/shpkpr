# third-party imports
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


def _update_property_if_changed(app, prop_name, value):
    """Update application property only if changed.
    """
    updated = False
    if value is not None and not getattr(app, prop_name) == value:
        updated = True
        setattr(app, prop_name, value)
    return app, updated


@click.command('scale', short_help='Scale application resources.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@pass_context
def cli(ctx, instances, mem, cpus, application):
    """Scale application resources to specified levels."""
    _app = ctx.marathon_client.get_application(application)

    _updated = False
    for prop_name in ['instances', 'mem', 'cpus']:
        _app, __updated = _update_property_if_changed(_app, prop_name, locals().get(prop_name))
        if __updated:
            _updated = True

    if _updated:
        ctx.vlog('Scaling application: %s', application)
        ctx.vlog('=====================%s', '=' * len(application))
        ctx.marathon_client.deploy_application(_app)
