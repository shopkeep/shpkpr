# stdlib imports
import os
import sys

# third-party imports
import click

# local imports
from . import logger


CONTEXT_SETTINGS = dict(auto_envvar_prefix='SHPKPR')


cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'commands'))


class ShpkprCLI(click.MultiCommand):

    def list_commands(self, ctx):
        files = [f for f in os.listdir(cmd_folder) if f.endswith('.py')]
        return sorted([f[4:-3] for f in files if f.startswith('cmd_')])

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('shpkpr.commands.cmd_' + name, None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ShpkprCLI, context_settings=CONTEXT_SETTINGS)
def cli():
    """A tool to manage applications running on Marathon."""
    logger.configure()
