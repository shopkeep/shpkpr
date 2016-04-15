# third-party imports
import chronos
import mock


def test_no_args(runner):
    result = runner(['cron'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['cron', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Manage Chronos Jobs' in result.output


@mock.patch.object(chronos.ChronosClient, 'list')
def test_list(mock_chronos_client, runner):

    mock_chronos_client.return_value = [{'name': 'foo'}, {'name': 'bar'}]

    result = runner(['cron', 'list'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert 'foo' in result.output
    assert 'bar' in result.output
    assert result.exit_code == 0
