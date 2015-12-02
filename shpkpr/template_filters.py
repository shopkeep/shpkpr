# local imports
from shpkpr import exceptions


def filter_items(value, startswith=None, strip_prefix=False):
    """Jinja2 filter used to filter a dictionary's keys by specifying a
    required prefix.

    Returns a list of key/value tuples.

    Usage:
        {{ my_dict|filter_items }}
        {{ my_dict|filter_items("MY_PREFIX_") }}
        {{ my_dict|filter_items("MY_PREFIX_", True) }}
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

    Usage:
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

    Usage:
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
