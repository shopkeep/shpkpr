def test_no_args(runner):
    result = runner(['cron'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['cron', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Manage Chronos Jobs' in result.output
