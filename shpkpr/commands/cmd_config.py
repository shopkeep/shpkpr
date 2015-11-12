# third-party imports
import click

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import MarathonClient


@click.group('config', short_help='Manage application configuration', context_settings=CONTEXT_SETTINGS)
@pass_context
def cli(ctx):
    """Manage application configuration.
    """


@cli.command('list', short_help='List application configuration.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.marathon_url
@pass_context
def list(ctx, application_id, marathon_url):
    """List application configuration.
    """
    application = MarathonClient(marathon_url).get_application(application_id)
    for k, v in sorted(application.env.items()):
        ctx.log("%s=%s", k, v)


@cli.command('set', short_help='Set application configuration.', context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', nargs=-1)
@params.application
@params.marathon_url
@pass_context
def set(ctx, application_id, env_vars, marathon_url):
    """Set application configuration.
    """
    marathon_client = MarathonClient(marathon_url)
    application = marathon_client.get_application(application_id)
    env_vars = dict([(x[0], x[1]) for x in [y.split('=') for y in env_vars]])
    for k, v in env_vars.items():
        application.env[k] = v

    # redeploy the reconfigured application
    marathon_client.deploy_application(application)


@cli.command('unset', short_help='Unset application configuration.', context_settings=CONTEXT_SETTINGS)
@click.argument('keys', nargs=-1)
@params.application
@params.marathon_url
@pass_context
def unset(ctx, application_id, marathon_url, keys):
    """Unset application configuration.
    """
    marathon_client = MarathonClient(marathon_url)
    application = marathon_client.get_application(application_id)
    for key in keys:
        try:
            del application.env[key]
        except KeyError:
            pass

    # redeploy the reconfigured application
    marathon_client.deploy_application(application)
