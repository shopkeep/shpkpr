# stdlib imports
import copy
import json

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
    result = runner(["apps", "show"], env=env)
    _check_exits_non_zero(result)
    _check_output_contains(result, "Unable to retrieve application details from marathon: does not exist.")


@pytest.mark.integration
def test_deploy_custom_template(runner, env):
    _tmpl_path = "tests/fixtures/templates/marathon/test.json.tmpl"
    result = runner(["apps", "deploy", "-t", _tmpl_path, "RANDOM_LABEL=some_value"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_show_again(runner, env):
    result = runner(["apps", "show"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, '"id": "/%s"' % env['SHPKPR_APPLICATION'])


@pytest.mark.integration
def test_deploy_default_template(runner, env):
    cmd = ["apps",
           "deploy",
           "LABEL_RANDOM=some_value",
           "DOCKER_EXPOSED_PORT=8080",
           "MARATHON_HEALTH_CHECK_PATH=/"]
    result = runner(cmd, env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_show_yet_again(runner, env):
    result = runner(["apps", "show", "-a", env['SHPKPR_MARATHON_APP_ID']], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, '"id": "/%s"' % env['SHPKPR_MARATHON_APP_ID'])
    _check_output_contains(result, '"RANDOM": "some_value"')


@pytest.mark.integration
def test_run(runner, env):
    result = runner(["apps", "run", "env", "ENV_TESTY_MC_TESTFACE=testy"], env=env)
    _check_exits_zero(result)
    _check_output_contains(result, "TESTY_MC_TESTFACE=testy")


@pytest.mark.integration
def test_cron_show(runner, env):
    result = runner(["cron", "show"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_set(runner, env):
    _tmpl_path = 'tests/fixtures/templates/chronos/test-chronos.json.tmpl'
    result = runner(["cron", "set", "--template", _tmpl_path, "CHRONOS_JOB_NAME=shpkpr-test-job"], env=env)
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


@pytest.mark.integration
def test_cron_set_default_template(runner, env):
    cmd = ["cron",
           "set",
           "CHRONOS_JOB_NAME=shpkpr-test-job",
           "CHRONOS_OWNER=example@example.com",
           'CHRONOS_CMD=echo \\"Hello World!\\"']
    result = runner(cmd, env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_show_default_template_after_add(runner, env):
    result = runner(["cron", "show"], env=env)

    _check_output_contains(result, '"name": "shpkpr-test-job"')
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_delete_default_template(runner, env):
    result = runner(["cron", "delete", "shpkpr-test-job"], env=env)

    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_show_default_template_after_delete(runner, env):
    result = runner(["cron", "show"], env=env)

    _check_output_does_not_contain(result, '"name": "shpkpr-test-job"')
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_set_with_secrets(runner, env):
    _tmpl_path = 'tests/fixtures/templates/chronos/test-chronos-secrets.json.tmpl'
    result = runner(["cron", "set", "--template", _tmpl_path, "CHRONOS_JOB_NAME=shpkpr-test-job"], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_show_secrets_after_add(runner, env):
    result = runner(["cron", "show", "-j", "shpkpr-test-job"], env=env)

    env_vars = json.loads(result.output)[0].get("environmentVariables", [])
    assert {"name": "MY_SECRET", "value": "bar"} in env_vars
    _check_exits_zero(result)


@pytest.mark.integration
def test_cron_delete_secrets(runner, env):
    result = runner(["cron", "delete", "shpkpr-test-job"], env=env)

    _check_exits_zero(result)


@pytest.mark.integration
def test_bluegreen_deploy(runner, env):
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen.json.tmpl"
    result = runner(["apps", "deploy", "--strategy", "bluegreen", "-t", _tmpl_path], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_deployed(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-blue"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, "shpkpr-test/integration-test-bluegreen-blue")


@pytest.mark.integration
def test_bluegreen_deploy_with_existing_app(runner, env):
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen.json.tmpl"
    result = runner(["apps", "deploy", "--strategy", "bluegreen", "-t", _tmpl_path], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_swapped(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-green"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, "shpkpr-test/integration-test-bluegreen-green")


@pytest.mark.integration
def test_bluegreen_deploy_default_template(runner, env):
    cmd = ["apps",
           "deploy",
           "--strategy",
           "bluegreen",
           "DOCKER_EXPOSED_PORT=8080",
           "MARATHON_APP_ID=shpkpr-test/integration-test-bluegreen-default-template",
           "MARATHON_HEALTH_CHECK_PATH=/",
           "MARATHON_SERVICE_PORT=11092",
           "MARATHON_SERVICE_PORT_ALT=11093",
           "HAPROXY_VHOST=shpkpr-test-bgdt.somedomain.com"]
    result = runner(cmd, env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_default_template_deployed(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-default-template-blue"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, local_env["SHPKPR_APPLICATION"])


@pytest.mark.integration
def test_bluegreen_deploy_with_existing_app_default_template(runner, env):
    cmd = ["apps",
           "deploy",
           "--strategy",
           "bluegreen",
           "DOCKER_EXPOSED_PORT=8080",
           "MARATHON_APP_ID=shpkpr-test/integration-test-bluegreen-default-template",
           "MARATHON_HEALTH_CHECK_PATH=/",
           "MARATHON_SERVICE_PORT=11092",
           "MARATHON_SERVICE_PORT_ALT=11093",
           "HAPROXY_VHOST=shpkpr-test-bgdt.somedomain.com"]
    result = runner(cmd, env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_default_template_swapped(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-default-template-green"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, local_env["SHPKPR_APPLICATION"])


@pytest.mark.integration
def test_bluegreen_autoports_deploy(runner, env):
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen-autoports.json.tmpl"
    result = runner(["apps", "deploy", "--strategy", "bluegreen", "-t", _tmpl_path], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_autoports_deploy(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-blue"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, "shpkpr-test/integration-test-bluegreen-blue")


@pytest.mark.integration
def test_bluegreen_autoports_deploy_with_existing_app(runner, env):
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen-autoports.json.tmpl"
    result = runner(["apps", "deploy", "--strategy", "bluegreen", "-t", _tmpl_path], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_autoports_swapped(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-green"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, "shpkpr-test/integration-test-bluegreen-green")


@pytest.mark.integration
def test_bluegreen_autoports_deploy_reset(runner, env):
    _tmpl_path = "tests/fixtures/templates/marathon/test-bluegreen-autoports.json.tmpl"
    result = runner(["apps", "deploy", "--strategy", "bluegreen", "-t", _tmpl_path], env=env)
    _check_exits_zero(result)


@pytest.mark.integration
def test_ensure_bluegreen_autoports_reset(runner, env):
    local_env = copy.deepcopy(env)
    local_env["SHPKPR_APPLICATION"] = "shpkpr-test/integration-test-bluegreen-blue"

    result = runner(["apps", "show"], env=local_env)
    _check_exits_zero(result)
    _check_output_contains(result, "shpkpr-test/integration-test-bluegreen-blue")
