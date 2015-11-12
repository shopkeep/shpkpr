# stdlib imports
import json
import os

# third-party imports
import click
from jinja2 import Template
from marathon.exceptions import NotFoundError
from marathon.models import MarathonApp

# local imports
from shpkpr import params
from shpkpr.cli import CONTEXT_SETTINGS
from shpkpr.cli import pass_context


@click.command('deploy', short_help='Deploy application from template.', context_settings=CONTEXT_SETTINGS)
@params.application
@params.cpus
@params.mem
@params.instances
@click.option('-t',
              '--template',
              type=click.File("r"),
              required=True,
              help="Path of the template to use for deployment.")
@pass_context
def cli(ctx, template, instances, mem, cpus, application):
    """Deploy application from template."""
    ctx.vlog('Deploying application: %s', application)
    ctx.vlog('=======================%s', '=' * len(application))

    # read and render deploy template using values from the environment
    _template = Template(template.read())
    _json = json.loads(_template.render(**os.environ))
    _app = MarathonApp.from_json(_json)

    # load existing config from marathon if available
    try:
        _existing = ctx.marathon_client.get_application(application)
    except NotFoundError:
        _existing = None

    # set instances value if specified
    if instances is not None:
        _app.instances = instances
    # otherwise use the existing value from marathon
    elif _existing is not None and not _app.instances:
        _app.instances = _existing.instances
    # set a default value for instances if not specified
    if _app.instances is None:
        _app.instances = 1

    # set mem value if specified
    if mem is not None:
        _app.mem = mem
    # otherwise use the existing value from marathon
    elif _existing is not None and not _app.mem:
        _app.mem = _existing.mem
    # set a default value for instances if not specified
    if _app.mem is None:
        _app.mem = 512

    # set cpus value if specified
    if cpus is not None:
        _app.cpus = cpus
    # otherwise use the existing value from marathon
    elif _existing is not None and not _app.cpus:
        _app.cpus = _existing.cpus
    # set a default value for cpus if not specified
    if _app.cpus is None:
        _app.cpus = 0.1

    # set the application ID to the value specified on the command line (unconditionally)
    _app.id = application

    ctx.vlog(json.dumps(json.loads(_app.to_json()), indent=4))
    ctx.marathon_client.deploy_application(_app)
