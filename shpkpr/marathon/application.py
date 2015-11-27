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

    READ_ONLY_PROPERTIES = ['tasks', 'tasksUnhealthy', 'deployments',
                            'tasksStaged', 'tasksRunning', 'tasksHealthy']

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
        jsonschema.validate(self.to_json(), self._schema)

        # since we use the PUT::/v2/apps/ endpoint for updates we need to ensure that
        # an application always has its ID set in the JSON to be posted.
        try:
            self['id']
        except KeyError:
            raise ValidationError('Missing `id` field.')

    def to_json(self, minimal=True):
        _out = {}
        for k, v in self._application.items():
            if minimal and v is None:
                continue
            if k in self.READ_ONLY_PROPERTIES:
                continue
            _out[k] = v
        return _out

    def get(self, key, default=None):
        try:
            return self._application[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        return self._application[key]

    def __setitem__(self, key, value):
        self._application[key] = value
