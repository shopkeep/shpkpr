# stdlib imports
import json
import os

# third-party imports
import jsonschema
from cached_property import cached_property

# local imports
from shpkpr import exceptions


def default_schema():
    """Path to the default schema used to validate application definitions
    before sending to marathon.
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "schema", "app.json")


class ValidationError(exceptions.ShpkprException):
    exit_code = 2

    def format_message(self):
        return 'Unable to validate application: %s' % self.message


class ApplicationError(exceptions.ShpkprException):
    exit_code = 2


class MarathonApplication(object):

    DEFAULT_SCHEMA_PATH = default_schema()

    def __init__(self, application_json, application_schema=None):
        self._application = application_json
        self._schema = application_schema

    @cached_property
    def schema(self):
        """Returns a JSON schema as a dictionary.

        If no schema was passed in, the default schema is loaded from disk.
        """
        if self._schema is not None:
            return self._schema
        with open(self.DEFAULT_SCHEMA_PATH, 'r') as f:
            return json.loads(f.read())

    @exceptions.rewrap(jsonschema.ValidationError, ValidationError)
    def validate(self):
        jsonschema.validate(self._application, self.schema)

        # since we use the PUT::/v2/apps/ endpoint for updates we need to ensure that
        # an application always has its ID set in the JSON to be posted.
        try:
            self['id']
        except KeyError:
            raise ValidationError('Missing `id` field.')

    def to_json(self):
        return self._application

    def get(self, key, default=None):
        try:
            return self._application[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        return self._application[key]

    def __setitem__(self, key, value):
        self._application[key] = value
