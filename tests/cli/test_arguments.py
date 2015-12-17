# third-party imports
import click
from click.testing import CliRunner

# local imports
from shpkpr.cli import arguments


def test_env_pairs():

    @click.command()
    @arguments.env_pairs
    def greet(env_pairs):
        for k, v in env_pairs.items():
            click.echo('(%s: %s)' % (k, v))

    result = CliRunner().invoke(greet, [
        'shp=kpr',
        'MYKEY=MYVALUE',
        'MY_OTHER_KEY=MY_OTHER=VALUE',
        'EMPTY_KEY',
    ])

    assert '(shp: kpr)' in result.output
    assert '(MYKEY: MYVALUE)' in result.output
    assert '(MY_OTHER_KEY: MY_OTHER=VALUE)' in result.output
    assert '(EMPTY_KEY: )' in result.output
