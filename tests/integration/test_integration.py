# third-party imports
import pytest


def _check_exits_zero(result):
    assert result.exit_code == 0


def _check_exits_non_zero(result):
    assert result.exit_code != 0


def _check_output_contains(result, match):
    assert match in result.output


def _check_output_does_not_contain(result, match):
    assert match not in result.output


@pytest.mark.integration
def test_help(runner, env):
    result = runner(["--help"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "Usage:")


@pytest.mark.integration
def test_show(runner, env):
    result = runner(["show"], env=env)
    _check_exits_non_zero(result)
    _check_output_contains(result, "Unable to retrieve application details from marathon: does not exist.")


@pytest.mark.integration
def test_deploy(runner, env):
    result = runner(["deploy", "-t", "tests/test.json.tmpl", "RANDOM_LABEL=some_value"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_show_again(runner, env):
    result = runner(["show"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "ID:           %s" % env['SHPKPR_APPLICATION'])


@pytest.mark.integration
def test_cron_show(runner, env):
    result = runner(["cron", "show"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_set(runner, env):
    result = runner(
        [
         "cron", "set",
         "--template", "tests/test-chronos.json.tmpl",
         "CHRONOS_JOB_NAME=shpkpr-test-job",
        ],
        env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_show_after_add(runner, env):
    result = runner(["cron", "show"], env=env)

    _check_output_contains(result, '"name": "shpkpr-test-job"')
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_run(runner, env):
    result = runner(["cron", "run", "shpkpr-test-job"], env=env)

    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_delete_tasks(runner, env):
    result = runner(["cron", "delete-tasks", "shpkpr-test-job"], env=env)

    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_delete(runner, env):
    result = runner(["cron", "delete", "shpkpr-test-job"], env=env)

    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_show_after_delete(runner, env):
    result = runner(["cron", "show"], env=env)

    _check_output_does_not_contain(result, '"name": "shpkpr-test-job"')
    _check_exits_zero(result)
