# third-party imports
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import MarathonApplication


@click.command('scale', short_help='Scale application resources.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@pass_context
def cli(ctx, instances, mem, cpus, application_id):
    """Scale application resources to specified levels.
    """
    existing_application = ctx.marathon_client.get_application(application_id)
    application = MarathonApplication({'id': application_id})

    updated = False
    for k, v in [('instances', instances), ('cpus', cpus), ('mem', mem)]:
        if v is not None and not v == existing_application[k]:
            updated = True
            application[k] = v

    if updated:
        ctx.marathon_client.deploy_application(application).wait()
