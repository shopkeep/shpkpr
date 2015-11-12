"""Common parameter definitions that be be imported by individual commands.

Only those parameters used by more than one command are defined here in an
attempt to maintain consistency across commands. Unique paramters may still be
defined on individual command functions.
"""
# third-party imports
import click


# The --application parameter is common to almost all shpkpr commands
application = click.option(
    '-a', '--application',
    'application_id',
    envvar="SHPKPR_APPLICATION",
    required=True,
    help="ID/name of the application to scale.",
)

# The --cpus parameter is common to the deploy and scale commands
cpus = click.option(
    '-c', '--cpus',
    type=float,
    help="Number of CPUs to assign to each instance of the application.",
)

# The --mem parameter is common to the deploy and scale commands
mem = click.option(
    '-m', '--mem',
    type=int,
    help="Amount of RAM (in MB) to assign to each instance of the application.",
)

# The --instances parameter is common to the deploy and scale commands
instances = click.option(
    '-i', '--instances',
    type=int,
    help="Number of instances of the application to run.",
)
