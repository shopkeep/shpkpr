# third-party imports
import pytest

# local imports
from shpkpr import template_filters


def test_filter_items():
    values = template_filters.filter_items({"X": "a", "Y": "b", "Z": "c"})
    assert ("X", "a") in values
    assert ("Y", "b") in values
    assert ("Z", "c") in values


def test_filter_items_with_startswith():
    values = template_filters.filter_items({"_X": "a", "_Y": "b", "Z": "c"}, startswith="_")
    assert ("_X", "a") in values
    assert ("_Y", "b") in values
    assert ("Z", "c") not in values


def test_filter_items_with_startswith_strip_prefix():
    values = template_filters.filter_items({"_X": "a", "_Y": "b", "Z": "c"}, startswith="_", strip_prefix=True)
    assert ("X", "a") in values
    assert ("Y", "b") in values
    assert ("Z", "c") not in values


def test_filter_items_with_strip_prefix():
    values = template_filters.filter_items({"_X": "a", "_Y": "b", "Z": "c"}, strip_prefix=True)
    assert ("_X", "a") in values
    assert ("_Y", "b") in values
    assert ("Z", "c") in values


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
