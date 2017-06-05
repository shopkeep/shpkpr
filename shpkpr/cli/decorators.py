# stdlib imports
import uuid

# third-party imports
import click


class HiddenOption(click.Option):
    """Option type that suppresses any help output.
    """
    hidden = True

    def get_help_record(self, ctx):
        return


def multioption(options, name=None, callback=None):
    """Attaches multiple options to a command function and optionally attaches a
    callback to a hidden option that's fired after parsing of the embedded
    options.
    """
    def decorator(f):
        if callback is not None:
            # this option exists mainly so that it can fire the callback and
            # that means we probably don't want users to invoke it on the
            # command line, accidentally or otherwise. Set its CLI flag to a
            # random(ish) string and hide it from the application's help output.
            f = click.option(
                "--{0}".format(uuid.uuid4().hex), name,
                callback=callback,
                cls=HiddenOption,
            )(f)
        # wrap the decorated function in all embedded decorators (in reverse
        # order so that they execute in the correct order at runtime).
        for option in reversed(options):
            f = option(f)
        return f
    return decorator
