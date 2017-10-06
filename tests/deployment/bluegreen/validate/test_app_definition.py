# third-party imports
import pytest

# local imports
from shpkpr.deployment.bluegreen.validate import AppDefinitionValidator
from shpkpr.deployment.bluegreen.validate import ValidationError


@pytest.fixture
def valid_app_definition(json_fixture):
    return json_fixture("marathon/bluegreen_app_new")


def test_valid_app(valid_app_definition):
    """Test that an app validates successfully when all the required labels are
    present.
    """
    validator = AppDefinitionValidator()
    try:
        validator.validate(valid_app_definition)
    except ValidationError as e:
        pytest.fail(e)


@pytest.fixture(params=[
    ["HAPROXY_DEPLOYMENT_GROUP"]
])
def invalid_app_definition(json_fixture, request):
    app_definition = json_fixture("marathon/bluegreen_app_new")
    for label in request.param:
        del(app_definition['labels'][label])
    return app_definition


def test_invalid_app(invalid_app_definition):
    """Test that an app fails validation when one or more required labels are
    missing.
    """
    validator = AppDefinitionValidator()
    with pytest.raises(ValidationError):
        validator.validate(invalid_app_definition)
