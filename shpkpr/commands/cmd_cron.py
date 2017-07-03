# stdlib imports
import logging

# third-party imports
import click

# local imports
from shpkpr.cli import arguments, options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template
from shpkpr.vault import resolve_secrets


logger = logging.getLogger(__name__)


@click.group('cron', context_settings=CONTEXT_SETTINGS)
def cli():
    """Manage Chronos jobs.
    """


@cli.command('show', short_help='List Chronos Jobs as json', context_settings=CONTEXT_SETTINGS)
@options.chronos_client
@options.job_name
@options.output_formatter
def show(chronos_client, job_name, output_formatter, **kw):
    """List application configuration.
    """
    jobs = chronos_client.list()

    if job_name is None:
        payload = jobs
    else:
        payload = _find_job(jobs, job_name)
    logger.info(output_formatter.format(payload))


def _inject_secrets(template, secrets):
    """Given an object containing secrets, inject them into a Chronos job prior
    to deployment.
    """
    if not template.get("environmentVariables"):
        template["environmentVariables"] = []
    for key, secret in secrets.items():
        template["environmentVariables"].append({
            "name": key,
            "value": secret,
        })
    return template


@cli.command('set', short_help='Add or Update a Chronos Job', context_settings=CONTEXT_SETTINGS)
@arguments.env_pairs
@options.chronos_client
@options.vault_client
@options.template_names
@options.template_path
@options.env_prefix
def set(chronos_client, vault_client, template_path, template_names, env_prefix, env_pairs, **kw):
    """Add or Update a job in chronos.
    """
    # use the default template if none was specified
    if not template_names:
        template_names = ["chronos/default/job.json.tmpl"]

    values = load_values_from_environment(prefix=env_prefix, overrides=env_pairs)
    current_jobs = chronos_client.list()

    for template_name in template_names:
        rendered_template = render_json_template(template_path, template_name, **values)
        resolved_secrets = resolve_secrets(vault_client, rendered_template)
        rendered_template = _inject_secrets(rendered_template, resolved_secrets)
        if _find_job(current_jobs, rendered_template['name']):
            chronos_client.update(rendered_template)
        else:
            chronos_client.add(rendered_template)


@cli.command('delete', short_help='Deletes a Job from Chronos', context_settings=CONTEXT_SETTINGS)
@arguments.job_name
@options.chronos_client
def delete(chronos_client, job_name, **kw):
    chronos_client.delete(job_name)


@cli.command('delete-tasks', short_help='Terminate all tasks for a Chronos Job.', context_settings=CONTEXT_SETTINGS)
@arguments.job_name
@options.chronos_client
def delete_tasks(chronos_client, job_name, **kw):
    chronos_client.delete_tasks(job_name)


@cli.command('run', short_help='Runs a Chronos Job', context_settings=CONTEXT_SETTINGS)
@arguments.job_name
@options.chronos_client
def run(chronos_client, job_name, **kw):
    chronos_client.run(job_name)


def _find_job(jobs, job_name):
    return list(filter(lambda j: job_name == j["name"], jobs))
