"""Templating related utilities
"""
# stdlib imports
import json
import os

# third-party imports
import jinja2

# local imports
from shpkpr import exceptions
from shpkpr import template_filters


class InvalidJSONError(exceptions.ShpkprException):
    """Raised when a template can be rendered successfully but does not parse
    as valid JSON afterwards.
    """
    exit_code = 2

    def format_message(self):
        return 'Unable to parse rendered template as JSON, check variables'


class UndefinedError(exceptions.ShpkprException):
    """Raised when a template contains a placeholder for a variable that
    wasn't included in the context dictionary passed in at render time.
    """
    exit_code = 2

    def format_message(self):
        return 'Unable to render template: %s' % self.message


class MissingTemplateError(exceptions.ShpkprException):
    """Raised when a template cannot be loaded for any reason.
    """
    exit_code = 2

    def format_message(self):
        return 'Unable to load template from disk: %s' % self.message


def load_values_from_environment(prefix="", overrides=None):
    """Reads values from the environment.

    If ``prefix`` is a non-empty string, only environment variables with the
    given prefix will be returned. The prefix, if given, will be stripped from
    any returned keys.

    If ``overrides`` is a dict-like object, the key/value pairs it contains
    will be added to the returned dictionary. Any values specified by
    overrides will take precedence over values pulled from the environment
    where the key names clash.
    """
    values = {}

    # add a trailing underscore to the prefix if there isn't one
    prefix = prefix + "_" if prefix and not prefix.endswith("_") else prefix

    # load values from the environment
    for k, v in os.environ.items():
        if k.startswith(prefix):
            values[k.replace(prefix, "", 1)] = v

    # add override values if any passed in
    try:
        for k, v in overrides.items():
            values[k] = v
    except AttributeError:
        pass

    return values


@exceptions.rewrap(ValueError, InvalidJSONError)
@exceptions.rewrap(jinja2.UndefinedError, UndefinedError)
@exceptions.rewrap(jinja2.TemplateNotFound, MissingTemplateError)
def render_json_template(template_path, template_name, **values):
    """Initialise a jinja2 template and render it with the passed-in values.

    The template, once rendered is treated as JSON and converted into a python
    dictionary. If the template is not valid JSON after rendering then an
    exception will be raised.

    If a template defines a placeholder for a variable that is not included in
    `values` an `UndefinedError` will be raised.

    ``template_path`` should be the base directory in which your templates are
    stored.
    ``template_name`` is the name (path) of the template being used to render.
    ``values`` should be regular keyword arguments to the function which will
    be passed to the template at render time.
    """
    # shpkpr ships with a number of built-in templates for each deployment type,
    # so we need to tell jinja where to look for them
    here = os.path.dirname(os.path.abspath(__file__))
    built_in_template_path = os.path.join(here, "resources", "templates")

    # build a new Jinja2 environment so we can inject some custom filters into
    # the template we're rendering.
    template_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        loader=jinja2.FileSystemLoader([
            built_in_template_path,
            template_path,
        ]),
    )
    template_env.filters['filter_items'] = template_filters.filter_items
    template_env.filters['require_int'] = template_filters.require_int
    template_env.filters['require_float'] = template_filters.require_float
    template_env.filters['slugify'] = template_filters.slugify

    template = template_env.get_template(template_name)
    rendered_template = template.render(_all_env=values, **values)
    return json.loads(rendered_template)
