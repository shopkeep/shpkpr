# third-party imports
import pytest
from freezegun import freeze_time

# local imports
from shpkpr.deployment.bluegreen.prepare import prepare_app_definition


@pytest.fixture
@freeze_time("2011-11-11T11:11:11.111111Z")
def app_definition(json_fixture):
    """Prepare an app definition for deployment.

    This fixture prepares an app and assumes that no existing stack is present
    on Marathon.
    """
    app_definition_fixture = json_fixture("marathon/bluegreen_app_new")
    app_states_fixture = json_fixture("valid_apps")
    return prepare_app_definition(app_definition_fixture, None, app_states_fixture['apps'])


def test_color(app_definition):
    """Test that the app's color is set as a label
    """
    actual = app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR']
    expected = "blue"

    assert actual == expected


def test_id(app_definition):
    """Test that the app's ID is correctly transformed
    """
    actual = app_definition['id']
    expected = "my-app-blue"

    assert actual == expected


def test_docker_service_port(app_definition):
    """Test that the service port is set correctly when using docker
    """
    actual = app_definition['container']['docker']['portMappings'][0]['servicePort']
    expected = 11090

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


def test_labels_deployment_started_at(app_definition):
    """Test that a timestamp is correctly added to the app's labels
    """
    actual = app_definition['labels']['HAPROXY_DEPLOYMENT_STARTED_AT']
    expected = "2011-11-11T11:11:11.111111"

    assert actual == expected
