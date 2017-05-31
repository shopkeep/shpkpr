# third-party imports
import click

# local imports
from shpkpr.cli import arguments
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.deployment import BlueGreenDeployment
from shpkpr.deployment import StandardDeployment
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


def _validate_strategy_bluegreen(marathon_lb_client, **kw):
    if marathon_lb_client is None:
        msg = 'Missing option "--marathon_lb_url".'
        raise click.UsageError(msg)


STRATEGIES = {
    "standard": {
        "executor": StandardDeployment,
        "validator": lambda **kw: None,
        "default_template": "marathon/default/standard.json.tmpl",
    },
    "bluegreen": {
        "executor": BlueGreenDeployment,
        "validator": _validate_strategy_bluegreen,
        "default_template": "marathon/default/bluegreen.json.tmpl",
    },
}


@click.command('deploy',
               short_help='Deploy an application to Marathon.',
               context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.force
@options.template_names
@options.template_path
@options.env_prefix
@options.timeout
@options.deployment_strategy
@options.marathon_lb_client
@options.marathon_client
def cli(marathon_client, marathon_lb_client, deployment_strategy, timeout,
        env_prefix, template_path, template_names, force, env_pairs, **kw):
    """Deploy application from template.
    """
    # select the appropriate deployment strategy
    strategy = STRATEGIES[deployment_strategy]

    # use the default template if none was specified
    if not template_names:
        template_names = [strategy["default_template"]]

    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    rendered_templates = []
    for template_name in template_names:
        rendered_templates.append(render_json_template(template_path, template_name, **values))

    # perform some extra pre-flight validation if required, and execute the
    # deployment, blocking until complete.
    deployment_params = {"marathon_client": marathon_client,
                         "marathon_lb_client": marathon_lb_client,
                         "timeout": timeout,
                         "app_definitions": rendered_templates}
    strategy["validator"](**deployment_params)
    strategy["executor"](**deployment_params).execute(force)
