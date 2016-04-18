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
def test_show(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = json_fixture("chronos_jobs")

    result = runner(['cron', 'show'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert '"name": "foo-job"' in result.output
    assert '"name": "bar-job"' in result.output
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'list')
def test_show_job_name(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = json_fixture("chronos_jobs")

    result = runner(['cron', 'show', '--job-name', 'foo-job'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert '"name": "foo-job"' in result.output
    assert '"name": "bar-job"' not in result.output
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'add')
def test_add(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = True

    result = runner(['cron', 'add', '--template', 'tests/test-chronos.json.tmpl'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'add')
def test_add_multiple(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(
        ['cron', 'add',
         '--template', 'tests/test-chronos.json.tmpl',
         '--template', 'tests/test-chronos-2.json.tmpl'],
        env={
            'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        },
    )

    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'delete')
def test_delete(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "delete", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0


@mock.patch.object(chronos.ChronosClient, 'delete_tasks')
def test_delete_tasks(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "delete-tasks", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0
