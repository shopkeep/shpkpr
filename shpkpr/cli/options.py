"""Option parameter definitions for shpkpr.

All option parameters should be defined in this module, commands should not
define their options directly, instead all options should be defined here and
imported as required. This helps maintain consistency where a single option is
used for multiple commands.
"""
# stdlib imports
import os
from distutils.version import StrictVersion

# third-party imports
import click
import hvac
from chronos import ChronosClient
from six.moves.urllib import parse

# local imports
from shpkpr.cli.decorators import multioption
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.formatter import OutputFormatter
from shpkpr.marathon import MarathonClient
from shpkpr.marathon_lb import MarathonLBClient


application_id = click.option(
    '-a', '--application',
    'application_id',
    envvar="{0}_APPLICATION".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    help=(
        "ID of the Marathon application to target. This should be the full "
        "path of the application (including slashes) e.g. ``/mygroup/myapp``. "
        "The first/root slash is optional, shpkpr will add it if missing."
    ),
)


dry_run = click.option(
    '--dry-run',
    is_flag=True,
    help=(
        "Enables \"dry run\" mode. When enabled, shpkpr will avoid making "
        "changes to any remote systems. This can be used to safely test "
        "deployments or jobs before performing any destructive operations. "
        "Exactly what constitues a \"dry run\" varies by operation type and "
        "deployment strategy, see command documentation for further "
        "information."
    ),
)


env_prefix = click.option(
    '-e', '--env-prefix',
    'env_prefix',
    default=CONTEXT_SETTINGS['auto_envvar_prefix'],
    show_default=True,
    help="Prefix used to filter environment variables used for templating.",
)


force = click.option(
    '--force',
    is_flag=True,
    help='Force update even if a deployment is in progress.',
)


deployment_strategy = click.option(
    '--strategy',
    'deployment_strategy',
    type=click.Choice(["standard", "bluegreen"]),
    help='Deployment strategy to utilise.',
    envvar="{0}_DEPLOYMENT_STRATEGY".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default="standard",
    show_default=True,
)


template_path = click.option(
    '--template-dir',
    'template_path',
    envvar="{0}_TEMPLATE_DIR".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    type=str,
    default=os.getcwd(),
    help="Base directory in which your templates are stored.",
)


template_names = click.option(
    '-t', '--template',
    'template_names',
    envvar="{0}_TEMPLATES".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    type=str,
    help="Path of the template to use for deployment.",
    multiple=True,
)

chronos_url = click.option(
    '--chronos-url',
    'chronos_url',
    envvar="{0}_CHRONOS_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help='URL of the Chronos endpoint to use',
    callback=lambda c, p, v: parse.urlparse(v, scheme="https"),
)


def _validate_chronos_version(ctx, param, value):
    """chronos-python requires a version "prefix" to be used, so we convert the
    target Chronos version to the appropriate prefix.
    """
    if StrictVersion(value) >= StrictVersion('3.0.0'):
        return 'v1'
    return None


chronos_version = click.option(
    '--chronos-version',
    'chronos_version',
    envvar="{0}_CHRONOS_VERSION".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=False,
    help='Verson of the Chronos endpoint to use',
    default='3.0.2',
    show_default=True,
    callback=_validate_chronos_version,
)

job_name = click.option(
    '-j', '--job-name',
    type=str,
    help='Restrict command to specific job.',
)


marathon_lb_client = click.option(
    '--marathon-lb-url',
    'marathon_lb_client',
    envvar="{0}_MARATHON_LB_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default=None,
    help="URL for Marathon-LB used during blue/green deployment.",
    callback=lambda c, p, v: None if v is None else MarathonLBClient(v)
)


timeout = click.option(
    '--timeout',
    'timeout',
    type=int,
    help='Maximum amount of time (in seconds) to wait for a deployment to finish before aborting.',
    envvar="{0}_TIMEOUT".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default=300,
    show_default=True,
)

output_formatter = click.option(
    '--output-format',
    'output_formatter',
    type=click.Choice(["json", "yaml"]),
    help='Serialization format to use when printing config data to stdout.',
    envvar="{0}_OUTPUT_FORMAT".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default="json",
    show_default=True,
    callback=lambda c, p, v: OutputFormatter(v)
)


def _validate_authentication(ctx, url, service_name):
    """Validates that authentication-related options required to initialise
    marathon/chronos clients have been set properly and securely.
    """
    allow_insecure_auth = ctx.params["allow_insecure_auth"]
    username = ctx.params["username"]
    password = ctx.params["password"]

    insecure_configuration = all([
        bool(username) or bool(password),
        not url.startswith("https://"),
        not allow_insecure_auth,
    ])

    if insecure_configuration:
        raise click.UsageError(
            "HTTPS is strongly recommended when using basic authentication (as "
            "credentials are sent unencrypted over the network).\n\nIf you "
            "want to allow insecure communications regardless, you can use the "
            "command-line flag: `--allow-insecure-auth`"
        )

    if username is not None and password is None:
        password = click.prompt("Please enter your {0} password".format(service_name))
    if password is not None and username is None:
        raise click.UsageError("A username is required to use HTTP Basic Authentication")


username = click.option(
    '--username',
    'username',
    type=str,
    help='Username used for HTTP Basic Authentication to Marathon/Chronos.',
    envvar="{0}_USERNAME".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default=None,
)

password = click.option(
    '--password',
    'password',
    type=str,
    help='Password used for HTTP Basic Authentication to Marathon/Chronos.',
    envvar="{0}_PASSWORD".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    default=None,
)

allow_insecure_auth = click.option(
    '--allow-insecure-auth',
    is_flag=True,
    help='Allow HTTP basic authentication when not using SSL.',
)

marathon_url = click.option(
    '--marathon-url',
    'marathon_url',
    envvar="{0}_MARATHON_URL".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    required=True,
    help="URL of the Marathon API to use.",
)


def _validate_marathon_client(ctx, _, __):
    """Validates that all options required to initialise a marathon client have
    been set properly and securely.

    A client is then initialised and returned to the command function.
    """
    _c = ctx.params
    _validate_authentication(ctx, _c["marathon_url"], "Marathon")
    return MarathonClient(_c["marathon_url"],
                          _c["username"],
                          _c["password"],
                          _c["dry_run"])


marathon_client = multioption(
    name='marathon_client',
    callback=_validate_marathon_client,
    options=[
        dry_run,
        allow_insecure_auth,
        username,
        password,
        marathon_url,
    ],
)


def _validate_chronos_client(ctx, _, __):
    """Validates that all options required to initialise a chronos client have
    been set properly and securely.

    A client is then initialised and returned to the command function.
    """
    _c = ctx.params
    _validate_authentication(ctx, parse.urlunparse(_c["chronos_url"]), "Chronos")
    return ChronosClient(_c["chronos_url"].netloc,
                         proto=_c["chronos_url"].scheme,
                         scheduler_api_version=_c["chronos_version"],
                         username=_c["username"],
                         password=_c["password"])


chronos_client = multioption(
    name='chronos_client',
    callback=_validate_chronos_client,
    options=[
        allow_insecure_auth,
        username,
        password,
        chronos_url,
        chronos_version,
    ],
)


vault_addr = click.option(
    '--vault-addr',
    'vault_addr',
    envvar="{0}_VAULT_ADDR".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    help="URL of the Vault API to use.",
)

vault_token = click.option(
    '--vault-token',
    'vault_token',
    envvar="{0}_VAULT_TOKEN".format(CONTEXT_SETTINGS['auto_envvar_prefix']),
    help="Token used to authenticate with Vault.",
)


def _validate_vault_client(ctx, _, __):
    """Validates that all options required to initialise a vault client have
    been set properly and securely.

    A client is then initialised and returned to the command function.
    """
    return hvac.Client(url=ctx.params['vault_addr'],
                       token=ctx.params['vault_token'])


vault_client = multioption(
    name='vault_client',
    callback=_validate_vault_client,
    options=[
        vault_addr,
        vault_token,
    ],
)
