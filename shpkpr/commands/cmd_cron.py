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


@cli.command('show', short_help='List Chronos Jobs as json', context_settings=CONTEXT_SETTINGS)
@options.chronos_client
@options.job_name
@pass_logger
def show(logger, chronos_client, job_name):
    """List application configuration.
    """
    jobs = chronos_client.list()

    if job_name is None:
        logger.log(_pretty_print(jobs))
    else:
        logger.log(_pretty_print(_find_job(jobs, job_name)))


@cli.command('set', short_help='Add or Update a Chronos Job', context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.chronos_client
@options.env_prefix
@options.template_names
@options.template_path
@options.env_prefix
def set(chronos_client, template_path, template_names, env_prefix, env_pairs):
    """Add or Update a job in chronos.
    """
    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    current_jobs = chronos_client.list()

    for template_name in template_names:
        rendered_template = render_json_template(template_path, template_name, **values)
        if _find_job(current_jobs, rendered_template['name']):
            chronos_client.update(rendered_template)
        else:
            chronos_client.add(rendered_template)


@cli.command('delete', short_help='Deletes a Job from Chronos', context_settings=CONTEXT_SETTINGS)
@arguments.job_name
@options.chronos_client
def delete(chronos_client, job_name):
    chronos_client.delete(job_name)


@cli.command('delete-tasks', short_help='Terminate all tasks for a specified Chronos Job.', context_settings=CONTEXT_SETTINGS)
@arguments.job_name
@options.chronos_client
def delete_tasks(chronos_client, job_name):
    chronos_client.delete_tasks(job_name)


@cli.command('run', short_help='Runs a Chronos Job', context_settings=CONTEXT_SETTINGS)
@arguments.job_name
@options.chronos_client
def run(chronos_client, job_name):
    chronos_client.run(job_name)


def _pretty_print(dict):
    """Pretty print a dict as a json structure
    """
    return json.dumps(dict, indent=4, sort_keys=True, separators=(',', ': '))


def _find_job(jobs, job_name):
    return list(filter(lambda j: job_name == j["name"], jobs))
