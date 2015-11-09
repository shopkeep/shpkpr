"""Common parameter definitions that be be imported by individual commands.

Only those parameters used by more than one command are defined here in an
attempt to maintain consistency across commands. Unique paramters may still be
defined on individual command functions.
"""
import click

application = click.option(
    '-a', '--application',
    required=True,
    help="ID/name of the application to scale.",
)

cpus = click.option(
    '-c', '--cpus',
    type=float,
    help="Number of CPUs to assign to each instance of the application.",
)

mem = click.option(
    '-m', '--mem',
    type=int,
    help="Amount of RAM (in MB) to assign to each instance of the application.",
)

instances = click.option(
    '-i', '--instances',
    type=int,
    help="Number of instances of the application to run.",
)
