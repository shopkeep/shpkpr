import mock

from shpkpr.vault import resolve_secrets


@mock.patch("shpkpr.cli.options.hvac.Client")
def test_resolve_secrets(mock_vault_client_class):
    mock_vault_data = {
        'secret/my_project/my_path': {
            'my_key': 'some_secret_info'
        }
    }
    mock_rendered_template = {
        'secrets': {
            'MY_SECRET_USING_REL_PATH': {'source': 'my_project/my_path:my_key'},
            'MY_SECRET_USING_FULL_PATH': {'source': 'secret/my_project/my_path:my_key'},
        }
    }

    def read_vault_data(path):
        secrets = mock_vault_data.get(path, None)
        return dict(data=secrets) if secrets else None

    mock_vault_client = mock_vault_client_class.return_value
    mock_vault_client.read.side_effect = read_vault_data

    result = resolve_secrets(mock_vault_client, mock_rendered_template)
    assert 'MY_SECRET_USING_REL_PATH' not in result
    assert result['MY_SECRET_USING_FULL_PATH'] == 'some_secret_info'
