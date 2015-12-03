# stdlib imports
import copy
import json
import os

# third-party imports
import jsonschema

# local imports
from shpkpr import exceptions


def schema_path(name):
    """Returns a path for one of the schema files distributed with shpkpr
    """
    this_directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_directory, "schema", "%s.json" % name)


def read_schema_from_file(path):
    """Read a JSON schema from disk and transform into a dict
    """
    with open(path, 'r') as f:
        schema = f.read()
    return json.loads(schema)


class ValidationError(exceptions.ShpkprException):
    exit_code = 2

    def format_message(self):
        return 'Unable to validate application: %s' % self.message


class Schema(object):

    def __init__(self, schema):
        self._schema = schema

    @exceptions.rewrap(jsonschema.ValidationError, ValidationError)
    def validate(self, application):
        """Validates the given application using the JSON schema
        """
        jsonschema.validate(application, self._schema)

    def strip(self, application):
        """Removes any top level properties from the application dictionary
        that aren't defined by the schema. This helps prevent the
        unintended use of unvalidated properties.
        """
        stripped_app = {}
        for key in self._schema.get('required', []):
            stripped_app[key] = copy.deepcopy(application[key])
        return stripped_app
