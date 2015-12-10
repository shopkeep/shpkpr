# stdlib imports
import sys

# third-party imports
import click


class Logger(object):

    def __init__(self):
        self.buffer = sys.stdout

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


pass_logger = click.make_pass_decorator(Logger, ensure=True)
