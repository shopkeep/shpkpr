# third-party imports
import pytest

# local imports
from shpkpr.deployment.bluegreen.prepare import prepare_app_definition
from shpkpr.deployment.bluegreen.prepare import _get_service_port
from shpkpr.deployment.bluegreen.prepare import _get_alt_service_port


@pytest.fixture
def prepared_app_definition(json_fixture, app_states_fixture):
    """Prepare an app definition for deployment.

    This fixture prepares an app and assumes that an existing stack is present
    on Marathon.
    """
    new_app_definition_fixture = json_fixture("marathon/bluegreen_app_auto_port_new")
    old_app_definition_fixture = json_fixture("marathon/bluegreen_app_existing")
    info_definition_fixture = json_fixture("marathon/info")

    return prepare_app_definition(new_app_definition_fixture,
                                  old_app_definition_fixture,
                                  app_states_fixture['apps'],
                                  info_definition_fixture)


@pytest.fixture
def app_states_fixture(json_fixture):
    app_states_fixture = json_fixture("valid_apps")
    return app_states_fixture


def test_color(prepared_app_definition):
    """Test that the app's color is set as a label
    """
    actual = prepared_app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR']
    expected = "green"

    assert actual == expected


def test_id(prepared_app_definition):
    """Test that the app's ID is correctly transformed
    """
    actual = prepared_app_definition['id']
    expected = "my-app-green"

    assert actual == expected


def test_docker_service_port(prepared_app_definition, app_states_fixture):
    """Test that the service port is set correctly when using docker
    """
    actual = prepared_app_definition['container']['docker']['portMappings'][0]['servicePort']

    app_states = app_states_fixture['apps']
    used_ports = []
    for prepared_app_definition in app_states:
        used_ports.append(_get_service_port(prepared_app_definition))
        used_ports.append(_get_alt_service_port(prepared_app_definition))
    assert actual not in used_ports


def test_labels_id(prepared_app_definition):
    """Test that the app's original ID is preserved as a label
    """
    actual = prepared_app_definition['labels']['HAPROXY_APP_ID']
    expected = "my-app"

    assert actual == expected
