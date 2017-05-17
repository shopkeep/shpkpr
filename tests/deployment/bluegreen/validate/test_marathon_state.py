# third-party imports
import mock
import pytest

# local imports
from shpkpr.deployment.bluegreen.validate import MarathonStateValidator
from shpkpr.deployment.bluegreen.validate import ValidationError


@pytest.fixture
def valid_app_definition(json_fixture):
    return json_fixture("marathon/bluegreen_app_new")


def test_valid_state(valid_app_definition):
    """Test that an app validates successfully when no existing stacks are
    present on Marathon.
    """
    marathon_client = mock.Mock()
    # we use a lambda here because mock interprets the empty list as list of
    # return values or exceptions to be raised and a single empty list causes an
    # error. the two options are wrapping the empty list in an outer list, or a
    # function that returns the empty list.
    marathon_client.list_applications.side_effect = lambda: []

    validator = MarathonStateValidator(marathon_client)
    try:
        validator.validate(valid_app_definition)
    except ValidationError as e:
        pytest.fail(e)


def test_valid_state_one_existing_stack(valid_app_definition, json_fixture):
    """Test that an app validates successfully when one existing stack is
    present on Marathon.
    """
    marathon_client = mock.Mock()
    marathon_client.list_applications.side_effect = lambda: [
        json_fixture("marathon/bluegreen_app_existing"),
    ]

    validator = MarathonStateValidator(marathon_client)
    try:
        validator.validate(valid_app_definition)
    except ValidationError as e:
        pytest.fail(e)


def test_invalid_state_two_existing_stacks(valid_app_definition, json_fixture):
    """Test that an app fails validation when more than one existing stack is
    present on Marathon.
    """
    marathon_client = mock.Mock()
    marathon_client.list_applications.side_effect = lambda: [
        json_fixture("marathon/bluegreen_app_existing"),
        json_fixture("marathon/bluegreen_app_existing"),
    ]

    validator = MarathonStateValidator(marathon_client)
    with pytest.raises(ValidationError):
        validator.validate(valid_app_definition)
