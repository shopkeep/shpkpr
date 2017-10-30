"""Argument parameter definitions for shpkpr.

All argument parameters should be defined in this module, commands should not
define their arguments directly, instead all arguments should be defined here
and imported as required. This helps maintain consistency where a single
argument is used for multiple commands.
"""
# third-party imports
import click


def _env_pairs_to_dict(ctx, param, value):
    """Converts a space-seperated list of key=value pairs into a Python
    dictionary.
    """
    d = {}
    for pair in [x.split('=', 1) for x in value]:
        if len(pair) == 1:
            d[pair[0]] = ''
        else:
            d[pair[0]] = pair[1]
    return d


command = click.argument(
    'command',
    nargs=1,
)

env_pairs = click.argument(
    'env_pairs',
    nargs=-1,
    callback=_env_pairs_to_dict,
)

job_name = click.argument(
    'job_name',
    nargs=1,
)
