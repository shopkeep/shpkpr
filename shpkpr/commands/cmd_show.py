# stdlib imports
import json

# third-party import
import click
import yaml

# local imports
from shpkpr.cli import options
from shpkpr.cli.entrypoint import CONTEXT_SETTINGS
from shpkpr.cli.logger import pass_logger


@click.command('show', short_help='Show application details.', context_settings=CONTEXT_SETTINGS)
@options.output_format
@options.application_id
@options.marathon_client
@pass_logger
def cli(logger, marathon_client, application_id, output_format):
    """Shows detailed information for one or more applications.
    """
    if application_id is None:
        payload = marathon_client.list_applications()
    else:
        payload = marathon_client.get_application(application_id)
    _pretty_print(logger, payload, output_format)


def _pretty_print(logger, payload, output_format):
    """Pretty print payload to stdout
    """
    formatters = {
        "json": lambda x: json.dumps(x, indent=4, sort_keys=True),
        "yaml": lambda x: yaml.dump(x, default_flow_style=False),
    }
    return logger.log(formatters[output_format](payload))
