# third-party imports
import pytest


def _check_exits_zero(result):
    assert result.exit_code == 0


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
def test_list(runner, env):
    result = runner(["list"], env=env)
    _check_exits_zero(result)
    _check_output_does_not_contain(result, env['SHPKPR_APPLICATION'])


@pytest.mark.integration
def test_deploy(runner, env):
    result = runner(["deploy", "-t", "tests/test.json.tmpl", "RANDOM_LABEL=some_value"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_list_again(runner, env):
    result = runner(["list"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, env['SHPKPR_APPLICATION'])


@pytest.mark.integration
def test_show(runner, env):
    result = runner(["show"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "ID:           %s" % env['SHPKPR_APPLICATION'])


@pytest.mark.integration
def test_scale(runner, env):
    result = runner(["scale", "--instances=3", "--cpus=0.1", "--mem=512"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_show_again(runner, env):
    result = runner(["show"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "Instances:    %s" % 3)
    _check_output_contains(result, "CPUs:         %s" % 0.1)
    _check_output_contains(result, "RAM:          %s" % 512)


@pytest.mark.integration
def test_scale_again(runner, env):
    result = runner(["scale", "--instances=2", "--cpus=0.1", "--mem=256"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_show_yet_again(runner, env):
    result = runner(["show"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "Instances:    %s" % 2)
    _check_output_contains(result, "CPUs:         %s" % 0.1)
    _check_output_contains(result, "RAM:          %s" % 256)


@pytest.mark.integration
def test_config_list(runner, env):
    result = runner(["config", "list"], env=env)
    _check_exits_zero(result)
    _check_output_does_not_contain(result, "SOMEVALUE")
    _check_output_does_not_contain(result, "SOMEOTHERVALUE")


@pytest.mark.integration
def test_config_set(runner, env):
    result = runner(["config", "set", "SOMEVALUE=some-key", "SOMEOTHERVALUE=some-other-key"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_config_list_again(runner, env):
    result = runner(["config", "list"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "SOMEVALUE=some-key")
    _check_output_contains(result, "SOMEOTHERVALUE=some-other-key")


@pytest.mark.integration
def test_config_unset(runner, env):
    result = runner(["config", "unset", "SOMEVALUE", "SOMEOTHERVALUE"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_config_list_yet_again(runner, env):
    result = runner(["config", "list"], env=env)
    _check_exits_zero(result)
    _check_output_does_not_contain(result, "SOMEVALUE")
    _check_output_does_not_contain(result, "SOMEOTHERVALUE")


@pytest.mark.integration
def test_logs(runner, env):
    result = runner(["logs", "-n", "10"], env=env)
    _check_exits_zero(result)


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
