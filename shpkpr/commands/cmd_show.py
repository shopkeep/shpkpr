# third-party import
import click

# local imports
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.command('show', short_help='Show application details.', context_settings=CONTEXT_SETTINGS)
@options.application_id
@options.marathon_client
@pass_logger
def cli(logger, marathon_client, application_id):
    """Shows detailed information for a single application.
    """
    application = marathon_client.get_application(application_id)
    _pretty_print(logger, application)


def _pretty_print(logger, application):
    """Pretty print application details to stdout
    """
    logger.log("ID:           %s", application['id'].lstrip('/'))
    logger.log("CPUs:         %s", application['cpus'])
    logger.log("RAM:          %s", application['mem'])
    logger.log("Instances:    %s", application['instances'])
    logger.log("Docker Image: %s", application['container']['docker']['image'])
    logger.log("Version:      %s", application['version'])
    logger.log("Status:       %s", _app_status(logger, application))
    logger.log("")
    logger.log("Tasks:")
    for task in application['tasks']:
        logger.log("- ID:   %s", task['id'])
        for port in task['ports']:
            logger.log("  Host: %s:%d", task['host'], port)


def _app_status(logger, application):
    """Returns a nicely formatted string we can use to display application health on the CLI.
    """
    if len(application['deployments']) > 0:
        return logger.style("DEPLOYING", fg='yellow')
    if application['tasksRunning'] == 0:
        return logger.style("SUSPENDED", fg='blue')
    if application['tasksUnhealthy'] > 0:
        return logger.style("UNHEALTHY", fg='red')
    return logger.style("HEALTHY", fg='green')
