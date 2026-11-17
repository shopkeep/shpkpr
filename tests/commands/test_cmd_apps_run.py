# third-party imports
import mock
import pytest


@pytest.mark.parametrize('exit_code', [0, 42])
@mock.patch('shpkpr.commands.cmd_apps.resolve_secrets', return_value={})
@mock.patch('shpkpr.commands.cmd_apps.render_json_template')
@mock.patch('shpkpr.commands.cmd_apps.docker.from_env')
def test_run_negotiates_docker_api_version(mock_from_env, mock_render, mock_secrets, runner, exit_code):
    mock_render.return_value = {
        'id': 'test-app',
        'container': {'docker': {'image': 'example/test:latest'}},
        'env': {'FOO': 'bar'},
    }
    container = mock_from_env.return_value.containers.run.return_value
    container.logs.return_value = [b'test output']
    container.wait.return_value = {'StatusCode': exit_code}

    result = runner(['apps', 'run', 'sleep 10'], env={
        'SHPKPR_VAULT_ADDR': 'http://localhost:8200',
        'SHPKPR_VAULT_TOKEN': 'test-token',
    })

    assert result.exit_code == exit_code
    mock_from_env.assert_called_once_with(version='auto')
    mock_from_env.return_value.containers.run.assert_called_once_with(
        'example/test:latest', 'sleep 10', detach=True, auto_remove=True,
        environment={'FOO': 'bar'},
    )
