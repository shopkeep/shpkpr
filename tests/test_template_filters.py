# third-party imports
import pytest

# local imports
from shpkpr import template_filters


def test_require_int():
    i = template_filters.require_int("1")
    assert i == 1


def test_require_int_in_range():
    i = template_filters.require_int("1", min=0, max=5)
    assert i == 1


def test_require_int_not_an_int():
    with pytest.raises(template_filters.IntegerRequired):
        template_filters.require_int("abc")


def test_require_int_too_low():
    with pytest.raises(template_filters.IntegerTooSmall):
        template_filters.require_int("-1", min=0)


def test_require_int_too_high():
    with pytest.raises(template_filters.IntegerTooLarge):
        template_filters.require_int("1", max=0)


def test_require_float():
    i = template_filters.require_float("1")
    assert i == 1


def test_require_float_in_range():
    i = template_filters.require_float("1", min=0, max=5)
    assert i == 1


def test_require_float_not_an_float():
    with pytest.raises(template_filters.FloatRequired):
        template_filters.require_float("abc")


def test_require_float_too_low():
    with pytest.raises(template_filters.FloatTooSmall):
        template_filters.require_float("-1", min=0)


def test_require_float_too_high():
    with pytest.raises(template_filters.FloatTooLarge):
        template_filters.require_float("1", max=0)
