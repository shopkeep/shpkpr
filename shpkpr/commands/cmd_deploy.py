# third-party imports
import click
from marathon.exceptions import NotFoundError
from marathon.models import MarathonApp

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context
from shpkpr.marathon import DeploymentFailed
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


def _update_property_with_defaults(application, existing_application, prop_name, value, default):
    """Update application property only if changed.

    ``application`` is the application instance on which the property will be updated
    ``existing_application`` is the application instance that is currently deployed to marathon (or None if not
                             deployed)
    ``prop_name`` is the name of the property on ``application`` that will be updated
    ``value`` if not None will supercede values set anywhere else, this typically will come from the command line
    ``default`` is a value that in the absence of any other source will be used to provide a sensible default
    """
    # set property value if specified
    if value is not None:
        setattr(application, prop_name, value)
    # otherwise use the existing value from marathon
    elif existing_application is not None and not getattr(application, prop_name):
        setattr(application, prop_name, getattr(existing_application, prop_name))

    # set a default value for instances if not specified
    if getattr(application, prop_name) is None:
        setattr(application, prop_name, default)

    return application


@click.command('deploy', short_help='Deploy application from template.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@click.option('-t',
              '--template',
              'template_file',
              type=click.File("r"),
              required=True,
              help="Path of the template to use for deployment.")
@pass_context
def cli(ctx, template_file, instances, mem, cpus, application_id):
    """Deploy application from template.
    """
    # read and render deploy template using values from the environment
    values = load_values_from_environment(prefix=CONTEXT_SETTINGS['auto_envvar_prefix'])
    try:
        rendered_template = render_json_template(template_file, **values)
    except ValueError as e:
        raise click.ClickException("Invalid JSON: " + str(e))
    application = MarathonApp.from_json(rendered_template)

    # load existing config from marathon if available
    try:
        existing_application = ctx.marathon_client.get_application(application_id)
    except NotFoundError:
        existing_application = None

    # override values from the command line
    application = _update_property_with_defaults(application, existing_application, 'instances', instances, 1)
    application = _update_property_with_defaults(application, existing_application, 'mem', mem, 512)
    application = _update_property_with_defaults(application, existing_application, 'cpus', cpus, 0.1)

    # set the application ID to the value specified on the command line (unconditionally)
    application.id = application_id

    deployment = ctx.marathon_client.deploy_application(application)
    try:
        deployment.wait()
    except DeploymentFailed as e:
        raise click.ClickException(str(e))
