# third-party imports
import click

# local imports
from shpkpr.cli import arguments
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.group('config', short_help='Manage application configuration', context_settings=CONTEXT_SETTINGS)
@pass_logger
def cli(logger):
    """Manage application configuration.
    """


@cli.command('list', short_help='List application configuration.', context_settings=CONTEXT_SETTINGS)
@options.application_id
@options.marathon_client
@pass_logger
def list(logger, marathon_client, application_id):
    """List application configuration.
    """
    application = marathon_client.get_application(application_id)
    for k, v in sorted(application['env'].items()):
        logger.log("%s=%s", k, v)


@cli.command('set', short_help='Set application configuration.', context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.application_id
@options.force
@options.marathon_client
@pass_logger
def set(logger, marathon_client, force, application_id, env_pairs):
    """Set application configuration.
    """
    existing_application = marathon_client.get_application(application_id)
    application = {'id': application_id, 'env': existing_application['env']}

    for k, v in env_pairs.items():
        application['env'][k] = v

    # redeploy the reconfigured application
    marathon_client.deploy(application, force=force).wait()


@cli.command('unset', short_help='Unset application configuration.', context_settings=CONTEXT_SETTINGS)
@arguments.env_keys
@options.application_id
@options.force
@options.marathon_client
@pass_logger
def unset(logger, marathon_client, force, application_id, env_keys):
    """Unset application configuration.
    """
    existing_application = marathon_client.get_application(application_id)
    application = {'id': application_id, 'env': existing_application['env']}

    for key in env_keys:
        try:
            del application['env'][key]
        except KeyError:
            pass

    # redeploy the reconfigured application
    marathon_client.deploy(application, force=force).wait()
