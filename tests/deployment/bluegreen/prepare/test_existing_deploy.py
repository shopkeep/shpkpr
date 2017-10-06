# third-party imports
import pytest

# local imports
from shpkpr.deployment.bluegreen.prepare import prepare_app_definition


@pytest.fixture
def app_definition(json_fixture):
    """Prepare an app definition for deployment.

    This fixture prepares an app and assumes that an existing stack is present
    on Marathon.
    """
    new_app_definition_fixture = json_fixture("marathon/bluegreen_app_new")
    old_app_definition_fixture = json_fixture("marathon/bluegreen_app_existing")
    app_states_fixture = json_fixture("valid_apps")
    info_definition_fixture = json_fixture("marathon/info")
    return prepare_app_definition(new_app_definition_fixture,
                                  old_app_definition_fixture,
                                  app_states_fixture['apps'],
                                  info_definition_fixture)


def test_color(app_definition):
    """Test that the app's color is set as a label
    """
    actual = app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR']
    expected = "green"

    assert actual == expected


def test_id(app_definition):
    """Test that the app's ID is correctly transformed
    """
    actual = app_definition['id']
    expected = "my-app-green"

    assert actual == expected


def test_docker_service_port(app_definition):
    """Test that the service port is set correctly when using docker
    """
    actual = app_definition['container']['docker']['portMappings'][0]['servicePort']
    expected = 11091

    assert actual == expected


def test_labels_id(app_definition):
    """Test that the app's original ID is preserved as a label
    """
    actual = app_definition['labels']['HAPROXY_APP_ID']
    expected = "my-app"

    assert actual == expected


def test_labels_port(app_definition):
    """Test that the app's original port is preserved as a label
    """
    actual = app_definition['labels']['HAPROXY_0_PORT']
    expected = "11090"

    assert actual == expected


def test_labels_alt_port(app_definition):
    """Test that the app's original port is preserved as a label
    """
    actual = app_definition['labels']['HAPROXY_DEPLOYMENT_ALT_PORT']
    expected = "11091"

    assert actual == expected
