# stdlib imports
import json

# third-party imports
import click

# local imports
from shpkpr.cli import arguments, options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


@click.group('cron', short_help='Manage Chronos Jobs', context_settings=CONTEXT_SETTINGS)
@pass_logger
def cli(logger):
    """Manage Chronos Jobs.
    """


@cli.command('show', short_help='List names all jobs in Chronos', context_settings=CONTEXT_SETTINGS)
@options.chronos_url
@options.job_name
@pass_logger
def show(logger, chronos_client, job_name):
    """List application configuration.
    """
    jobs = chronos_client.list()

    if job_name is None:
        logger.log(_pretty_print(jobs))
    else:
        logger.log(_pretty_print(filter(lambda j: job_name == j['name'], jobs)))


@cli.command('add', short_help='Add a job to chronos', context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.chronos_url
@options.env_prefix
@options.template_names
@options.template_path
@options.env_prefix
@pass_logger
def add(logger, chronos_client, template_path, template_names, env_prefix, env_pairs):
    """Add a job to chronos.
    """
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    for template_name in template_names:
        chronos_client.add(render_json_template(template_path, template_name, **values))


def _pretty_print(dict):
    """Pretty print a dict as a json structure
    """
    return json.dumps(dict, indent=4, sort_keys=True, separators=(',', ': '))
