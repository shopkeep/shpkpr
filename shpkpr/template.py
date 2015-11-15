"""Templating related utilities
"""
# stdlib imports
import json
import os

# third-party imports
from jinja2 import Template


def load_values_from_environment(prefix=""):
    """Reads values from the environment.

    If ``prefix`` is a non-empty string, only environment variables with the
    given prefix will be returned. The prefix, if given, will be stripped from
    any returned keys.
    """
    # add a trailing underscore to the prefix if there isn't one
    prefix = prefix + "_" if prefix and not prefix.endswith("_") else prefix

    values = {}
    for k, v in os.environ.items():
        if k.startswith(prefix):
            values[k.replace(prefix, "", 1)] = v
    return values


def render_json_template(template_file, **values):
    """Initialise a jinja2 template and render it with the passed-in values.

    The template, once rendered is treated as JSON and converted into a python
    dictionary. If the template is not valid JSON after rendering then an
    exception will be raised.

    ``template_file`` should be a file-like object, opened for reading.
    ``values`` should be regular keyword arguments to the function which will
    be passed to the template at render time.
    """
    template = Template(template_file.read())
    rendered_template = template.render(**values)
    return json.loads(rendered_template)
