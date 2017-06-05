# stdlib imports
import functools
import sys

# third-party imports
import six
from click.exceptions import ClickException


class ShpkprException(ClickException):
    """Common base class for all exceptions raised explicitly by shpkpr.

    Exceptions which are subclasses of this type will be handled nicely by
    shpkpr and a human-readable error message will be displayed to the user
    before exiting with an appropriate non-zero exit code. Any exceptions
    raised which are not a subclass of this type will exit(1) and print a
    traceback to the user's console.
    """
    pass


def _args_from_exception(exception):
    """In Python 3 we can't guarantee that an exception will have a `message`
    property. This function ensures that we can extract *args and have it
    include at least one argument, regardless of the exception type passed-in.
    """
    if exception.args:
        return exception.args
    if hasattr(exception, "message"):
        return (exception.message,)
    return (str(exception),)


def rewrap(exceptions_to_catch, exception_to_rewrap_with=ShpkprException):
    """Decorator that catches exceptions of type `exceptions_to_catch` (can be
    a list) and rewraps them with the given `exception_to_rewrap_with` type
    before re-raising with the original stack trace.
    """
    def real_decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exceptions_to_catch:
                # the syntax for raising an exception with a traceback changed
                # in Python 3 and the python 2 version will cause the code to
                # throw a syntax error when parsed, so we use six to provide a
                # version agnostic `reraise` function we can use in all
                # environments.
                ei, tb = sys.exc_info()[1:]
                if six.PY2:
                    six.reraise(exception_to_rewrap_with, ei.message, tb)
                else:
                    ei_args = _args_from_exception(ei)
                    six.reraise(exception_to_rewrap_with, exception_to_rewrap_with(*ei_args), tb)
        return wrapper
    return real_decorator
