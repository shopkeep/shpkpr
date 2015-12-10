# third-party imports
import click

# local imports
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.command('scale', short_help='Scale application resources.', context_settings=CONTEXT_SETTINGS)
@options.application_id
@options.cpus
@options.mem
@options.instances
@options.marathon_client
@pass_logger
def cli(logger, marathon_client, instances, mem, cpus, application_id):
    """Scale application resources to specified levels.
    """
    existing_application = marathon_client.get_application(application_id)
    application = {'id': application_id}

    updated = False
    for k, v in [('instances', instances), ('cpus', cpus), ('mem', mem)]:
        if v is not None and not v == existing_application[k]:
            updated = True
            application[k] = v

    if updated:
        marathon_client.deploy_application(application).wait()
