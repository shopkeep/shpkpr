# local imports
from shpkpr import exceptions

# third-party imports
import slugify as libslugify


def filter_items(value, startswith=None, strip_prefix=False):
    """Jinja2 filter used to filter a dictionary's keys by specifying a
    required prefix.

    Returns a list of key/value tuples.

    .. code-block:: jinja

        {{ my_dict|filter_items }}
        {{ my_dict|filter_items("MY_PREFIX_") }}
        {{ my_dict|filter_items("MY_PREFIX_", True) }}

    This is most useful in combination with the special
    :ref:`_all_env <all_env>` variable that shpkpr injects into every template.
    For example, to iterate over only the template variables that start with
    ``LABEL_`` you could do:

    .. code-block:: jinja

        {% for k, v in _all_env|filter_items("LABEL_", strip_prefix=True) %}
            "{{k}}": "{{v}}",
        {% endfor %}

    """
    if startswith is not None:
        value = [x for x in value.items() if x[0].startswith(startswith)]
    else:
        value = value.items()

    if startswith is not None and strip_prefix:
        value = [(x[0].replace(startswith, "", 1), x[1]) for x in value]

    return value


class IntegerRequired(exceptions.ShpkprException):
    exit_code = 2


class IntegerTooSmall(exceptions.ShpkprException):
    exit_code = 2


class IntegerTooLarge(exceptions.ShpkprException):
    exit_code = 2


@exceptions.rewrap(ValueError, IntegerRequired)
def require_int(value, min=None, max=None):
    """Jinja2 filter used to enforce an integer type in a template.

    Accepts optional min/max constraints.

    .. code-block:: jinja

        {{ my_integer_value|require_int }}
        {{ my_integer_value|require_int(min=0) }}
        {{ my_integer_value|require_int(min=0, max=20) }}
        {{ my_integer_value|require_int(max=20) }}
    """
    value = int(value)

    # check the integer falls within the allowed range if set
    if min is not None and value < min:
        raise IntegerTooSmall("%d is smaller than the minimum allowed value of %d" % (value, min))
    if max is not None and value > max:
        raise IntegerTooLarge("%d is larger than the maximum allowed value of %d" % (value, max))

    return value


class FloatRequired(exceptions.ShpkprException):
    exit_code = 2


class FloatTooSmall(exceptions.ShpkprException):
    exit_code = 2


class FloatTooLarge(exceptions.ShpkprException):
    exit_code = 2


@exceptions.rewrap(ValueError, FloatRequired)
def require_float(value, min=None, max=None):
    """Jinja2 filter used to enforce an float type in a template.

    Accepts optional min/max constraints.

    .. code-block:: jinja

        {{ my_float_value|require_float }}
        {{ my_float_value|require_float(min=0) }}
        {{ my_float_value|require_float(min=0, max=20) }}
        {{ my_float_value|require_float(max=20) }}
    """
    value = float(value)

    # check the float falls within the allowed range if set
    if min is not None and value < min:
        raise FloatTooSmall("%f is smaller than the minimum allowed value of %f" % (value, min))
    if max is not None and value > max:
        raise FloatTooLarge("%f is larger than the maximum allowed value of %f" % (value, max))

    return value


def slugify(value, *args, **kwargs):
    """Jinja2 filter used to slugify a string.

    All arguments are passed directly to python-slugify_'s ``slugify``
    function, see the library's documentation_ for further information.

    .. code-block:: jinja

        {{ my_string|slugify }}
        {{ my_string|slugify(max_length=20) }}

    .. _python-slugify: https://pypi.python.org/pypi/python-slugify
    .. _documentation: https://github.com/un33k/python-slugify#how-to-use
    """
    return libslugify.slugify(value, *args, **kwargs)
