# third-party imports
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import MarathonClient


def _update_property_if_changed(application, prop_name, value):
    """Update application property only if changed.
    """
    updated = False
    if value is not None and not getattr(application, prop_name) == value:
        updated = True
        setattr(application, prop_name, value)
    return application, updated


@click.command('scale', short_help='Scale application resources.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@params.marathon_url
@pass_context
def cli(ctx, marathon_url, instances, mem, cpus, application_id):
    """Scale application resources to specified levels.
    """
    marathon_client = MarathonClient(marathon_url)
    application = marathon_client.get_application(application_id)

    updated = False
    for prop_name in ['instances', 'mem', 'cpus']:
        application, _updated = _update_property_if_changed(application, prop_name, locals().get(prop_name))
        if _updated:
            updated = True

    if updated:
        marathon_client.deploy_application(application)
