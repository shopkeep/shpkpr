# stdlib imports
import os
import sys

# third-party imports
import click
from cached_property import cached_property

# local imports
from shpkpr.marathon import MarathonClient
from shpkpr.mesos import MesosClient


CONTEXT_SETTINGS = dict(auto_envvar_prefix='SHPKPR')


class Context(object):

    def __init__(self):
        self.buffer = sys.stdout
        self.marathon_url = None
        self.mesos_master_url = None
        self._marathon_client = None
        self._mesos_client = None

    @cached_property
    def marathon_client(self):
        if not self.marathon_url:
            raise click.exceptions.UsageError("Missing option \"--marathon_url\".")

        return MarathonClient(self.marathon_url)

    @cached_property
    def mesos_client(self):
        if not self.mesos_master_url:
            raise click.exceptions.UsageError("Missing option \"--mesos_master_url\".")

        return MesosClient(self.mesos_master_url)

    def log(self, msg, *args, **kwargs):
        """Logs a message to stdout."""
        if args:
            msg %= args
        click.echo(msg, file=self.buffer, **kwargs)

    def style(self, msg, *args, **kwargs):
        """Wrapper around click.style to allow modules to access this
        functionality via the context object without having to depend on
        click.
        """
        return click.style(msg, *args, **kwargs)


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))


class ShpkprCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('shpkpr.commands.cmd_' + name, None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ShpkprCLI, context_settings=CONTEXT_SETTINGS)
@click.option('--marathon_url', help="URL of the Marathon API to use.")
@click.option('--mesos_master_url', help="URL of the Mesos master to use.")
@pass_context
def cli(ctx, mesos_master_url, marathon_url):
    """A tool to manage applications running on Marathon."""
    ctx.marathon_url = marathon_url
    ctx.mesos_master_url = mesos_master_url
