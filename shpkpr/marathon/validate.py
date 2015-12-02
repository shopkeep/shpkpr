# stdlib imports
import copy
import json
import os

# third-party imports
import jsonschema

# local imports
from shpkpr import exceptions


def load_schema(name):
    """Path to the default schema used to validate application definitions
    before sending to marathon.
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "schema", "%s.json" % name)


class ValidationError(exceptions.ShpkprException):
    exit_code = 2

    def format_message(self):
        return 'Unable to validate application: %s' % self.message


class SchemaValidator(object):

    def __init__(self, schema_path, strip=False):
        self._schema = self._read_schema_from_file(schema_path)
        self._strip = strip

    @exceptions.rewrap(jsonschema.ValidationError, ValidationError)
    def __call__(self, application):
        jsonschema.validate(application, self._schema)
        if not self._strip:
            return application
        return self.strip(application)

    def _read_schema_from_file(self, path):
        with open(path, 'r') as f:
            schema = f.read()
        return json.loads(schema)

    def strip(self, application):
        """Removes any top level properties from the application dictionary
        that haven't been validated by the schema. This helps prevent the
        unintended use of unvalidated properties.
        """
        stripped_app = {}
        for key in self._schema['required']:
            stripped_app[key] = copy.deepcopy(application[key])
        return stripped_app


validate_app = SchemaValidator(load_schema("app"), strip=True)
validate_deploy = SchemaValidator(load_schema("deploy"))
