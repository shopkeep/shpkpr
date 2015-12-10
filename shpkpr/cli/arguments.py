"""Argument parameter definitions for shpkpr.

All argument parameters should be defined in this module, commands should not
define their arguments directly, instead all arguments should be defined here
and imported as required. This helps maintain consistency where a single
argument is used for multiple commands.
"""
# third-party imports
import click


env_pairs = click.argument(
    'env_pairs',
    nargs=-1,
)


env_keys = click.argument(
    'env_keys',
    nargs=-1,
)
