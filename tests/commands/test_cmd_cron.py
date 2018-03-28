# third-party imports
import mock


def test_no_args(runner):
    result = runner(['cron'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_help(runner):
    result = runner(['cron', '--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Manage Chronos jobs' in result.output


@mock.patch("shpkpr.cli.options.ChronosClient.list")
def test_show(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = json_fixture("chronos_jobs")

    result = runner(['cron', 'show'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert '"name": "foo-job"' in result.output
    assert '"name": "bar-job"' in result.output
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.list")
def test_show_job_name(mock_chronos_client, runner, json_fixture):
    mock_chronos_client.return_value = json_fixture("chronos_jobs")

    result = runner(['cron', 'show', '--job-name', 'foo-job'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    assert '"name": "foo-job"' in result.output
    assert '"name": "bar-job"' not in result.output
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.list")
@mock.patch("shpkpr.cli.options.ChronosClient.add")
def test_set(mock_chronos_add, mock_chronos_list, runner, json_fixture):
    mock_chronos_list.return_value = []
    mock_chronos_add.return_value = True

    _tmpl_path = 'tests/fixtures/templates/chronos/test-chronos.json.tmpl'
    result = runner(['cron', 'set', '--template', _tmpl_path], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
    })

    assert mock_chronos_add.called
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.list")
@mock.patch("shpkpr.cli.options.ChronosClient.add")
def test_set_default_template(mock_chronos_add, mock_chronos_list, runner, json_fixture):
    mock_chronos_list.return_value = []
    mock_chronos_add.return_value = True

    result = runner(['cron', 'set'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
        'SHPKPR_CHRONOS_OWNER': 'shpkpr-test@example.com',
        'SHPKPR_CHRONOS_CMD': 'someprogram --run',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
    })

    assert mock_chronos_add.called
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.list")
@mock.patch("shpkpr.cli.options.ChronosClient.add")
def test_set_default_template_labels(mock_chronos_add, mock_chronos_list, runner, json_fixture):
    mock_chronos_list.return_value = []
    mock_chronos_add.return_value = True

    result = runner(['cron', 'set'], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
        'SHPKPR_CHRONOS_OWNER': 'shpkpr-test@example.com',
        'SHPKPR_CHRONOS_CMD': 'someprogram --run',
        'SHPKPR_LABEL_SOME_LABEL': 'some-value',
        'SHPKPR_DOCKER_REPOTAG': 'goexample/outyet:latest',
    })

    assert mock_chronos_add.called
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.list")
@mock.patch("shpkpr.cli.options.ChronosClient.add")
def test_set_multiple(mock_chronos_add, mock_chronos_list, runner):
    mock_chronos_list.return_value = []
    mock_chronos_add.return_value = True

    _tmpl_path = 'tests/fixtures/templates/chronos/test-chronos.json.tmpl'
    _tmpl_path_2 = 'tests/fixtures/templates/chronos/test-chronos-2.json.tmpl'
    result = runner(
        [
            'cron', 'set',
            '--template', _tmpl_path,
            '--template', _tmpl_path_2,
        ],
        env={
            'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
            'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
            'SHPKPR_CHRONOS_JOB_2_NAME': 'shpkpr-test-job-2',
        },
    )

    assert mock_chronos_add.called_twice
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.list")
@mock.patch("shpkpr.cli.options.ChronosClient.update")
@mock.patch("shpkpr.cli.options.ChronosClient.add")
def test_set_update(mock_chronos_add, mock_chronos_update, mock_chronos_list, runner):
    mock_chronos_list.return_value = [{'name': 'shpkpr-test-job'}]
    mock_chronos_update.return_value = True

    _tmpl_path = 'tests/fixtures/templates/chronos/test-chronos.json.tmpl'
    result = runner(['cron', 'set', '--template', _tmpl_path], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
        'SHPKPR_CHRONOS_JOB_NAME': 'shpkpr-test-job',
    })

    mock_chronos_add.assert_not_called()

    assert mock_chronos_update.called
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.delete")
def test_delete(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "delete", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.delete_tasks")
def test_delete_tasks(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "delete-tasks", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0


@mock.patch("shpkpr.cli.options.ChronosClient.run")
def test_run(mock_chronos_client, runner):
    mock_chronos_client.return_value = True

    result = runner(["cron", "run", "test-job"], env={
        'SHPKPR_CHRONOS_URL': "chronos.somedomain.com:4400",
    })

    mock_chronos_client.assert_called_with('test-job')
    assert result.exit_code == 0
