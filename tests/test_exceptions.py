# third-party imports
import pytest

# local imports
from shpkpr import exceptions


@exceptions.rewrap(ValueError)
def _this_doesnt_raise():
    """Dummy func for testing the exceptions.rewrap decorator
    """
    return 'something'


@exceptions.rewrap(ValueError)
def _this_raises_a_key_error():
    """Dummy func for testing the exceptions.rewrap decorator
    """
    return {}['non-existant-key']


@exceptions.rewrap(ValueError)
def _this_raises_a_value_error():
    """Dummy func for testing the exceptions.rewrap decorator
    """
    return int("banana for scale")


@exceptions.rewrap(ValueError, KeyError)
def _this_also_raises_a_value_error():
    """Dummy func for testing the exceptions.rewrap decorator
    """
    return int("I suggest you drop it, Mr. Data")


class ExceptionRaiser(object):
    """Dummy class for testing the exceptions.rewrap decorator
    """

    @exceptions.rewrap(KeyError)
    def this_raises_a_key_error(self):
        return {}['non-existant-key']

    @exceptions.rewrap(ValueError)
    def this_also_raises_a_key_error(self):
        return {}['non-existant-key']


def test_rewrap_func_doesnt_rewrap_uncaught_exception():
    with pytest.raises(KeyError):
        _this_raises_a_key_error()


def test_rewrap_func_raises_correct_exception():
    with pytest.raises(exceptions.ShpkprException):
        _this_raises_a_value_error()


def test_rewrap_func_raises_correct_exception_keyerror():
    with pytest.raises(KeyError):
        _this_also_raises_a_value_error()


def test_rewrap_method_raises_correct_exception():
    obj = ExceptionRaiser()
    with pytest.raises(exceptions.ShpkprException):
        obj.this_raises_a_key_error()


def test_rewrap_method_doesnt_rewrap_uncaught_exception():
    obj = ExceptionRaiser()
    with pytest.raises(KeyError):
        obj.this_also_raises_a_key_error()


def test_decorated_func_returns_as_normal_when_nothing_is_raised():
    assert _this_doesnt_raise() == 'something'
