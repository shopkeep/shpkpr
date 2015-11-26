# stdlib imports
import collections
import os

# third-party imports
import jsonschema

# local imports
from shpkpr import exceptions


def default_schema():
    """Path to the default schema used to validate application definitions
    before sending to marathon. The user can override this location on the
    command line.
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "schema.json")


class ValidationError(exceptions.ShpkprException):
    exit_code = 2

    def format_message(self):
        return 'Unable to validate application: %s' % self.message


class ApplicationError(exceptions.ShpkprException):
    exit_code = 2


class MarathonApplication(object):

    def __init__(self, application_json=None, application_schema=None):
        self._application = None
        self._schema = None

        if application_json is not None:
            if not isinstance(application_json, collections.Mapping):
                raise ApplicationError("`application_json` is not of type collections.Mapping")
            self._application = application_json

        if application_schema is not None:
            if not isinstance(application_schema, collections.Mapping):
                raise ApplicationError("`application_schema` is not of type collections.Mapping")
            self._schema = application_schema

    @exceptions.rewrap(jsonschema.ValidationError, ValidationError)
    def validate(self):
        if self._schema is None:
            return None
        if self._application is None:
            jsonschema.validate({}, self._schema)
        jsonschema.validate(self._application, self._schema)

    def to_json(self):
        return self._application

    def __getattr__(self, value):
        return getattr(self._application, value)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            setattr(self._application, key, value)
