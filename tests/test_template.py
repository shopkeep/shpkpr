# stdlib imports
import StringIO

# third-party imports
import pytest

# local imports
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template


def test_load_environment_vars_without_prefix(monkeypatch):
    monkeypatch.setenv('BANANA', 'bread')
    monkeypatch.setenv('STRAWBERRY', 'cheesecake')
    monkeypatch.setenv('APPLE_AND_BLACKCURRANT', 'crumble')

    values = load_values_from_environment()

    assert 'BANANA' in values
    assert values['BANANA'] == 'bread'
    assert 'STRAWBERRY' in values
    assert values['STRAWBERRY'] == 'cheesecake'
    assert 'APPLE_AND_BLACKCURRANT' in values
    assert values['APPLE_AND_BLACKCURRANT'] == 'crumble'


def test_load_environment_vars_with_prefix(monkeypatch):
    monkeypatch.setenv('BANANA', 'bread')
    monkeypatch.setenv('SHPKPR_STRAWBERRY', 'cheesecake')
    monkeypatch.setenv('SHPKPR_APPLE_AND_BLACKCURRANT', 'crumble')
    monkeypatch.setenv('SHPKPR_SHPKPR_APPLE_AND_BLACKCURRANT', 'crumble')

    values = load_values_from_environment("SHPKPR")

    assert 'BANANA' not in values
    assert 'STRAWBERRY' in values
    assert values['STRAWBERRY'] == 'cheesecake'
    assert 'APPLE_AND_BLACKCURRANT' in values
    assert values['APPLE_AND_BLACKCURRANT'] == 'crumble'
    assert 'SHPKPR_APPLE_AND_BLACKCURRANT' in values
    assert values['SHPKPR_APPLE_AND_BLACKCURRANT'] == 'crumble'


def test_load_environment_vars_with_prefix_with_trailing_underscore(monkeypatch):
    monkeypatch.setenv('BANANA', 'bread')
    monkeypatch.setenv('SHPKPR_STRAWBERRY', 'cheesecake')
    monkeypatch.setenv('SHPKPR_APPLE_AND_BLACKCURRANT', 'crumble')
    monkeypatch.setenv('SHPKPR_SHPKPR_APPLE_AND_BLACKCURRANT', 'crumble')

    values = load_values_from_environment("SHPKPR_")

    assert 'BANANA' not in values
    assert 'STRAWBERRY' in values
    assert values['STRAWBERRY'] == 'cheesecake'
    assert 'APPLE_AND_BLACKCURRANT' in values
    assert values['APPLE_AND_BLACKCURRANT'] == 'crumble'
    assert 'SHPKPR_APPLE_AND_BLACKCURRANT' in values
    assert values['SHPKPR_APPLE_AND_BLACKCURRANT'] == 'crumble'


def test_render_json_template_valid(monkeypatch):
    template_file = StringIO.StringIO('{"type_of_muffin": "{{ MUFFIN_TYPE }}"}')

    rendered_template = render_json_template(template_file, **{"MUFFIN_TYPE": "banana"})
    assert "type_of_muffin" in rendered_template
    assert rendered_template["type_of_muffin"] == "banana"


def test_render_json_template_invalid_json_unquoted_string():
    template_file = StringIO.StringIO('{"type_of_muffin": {{ MUFFIN_TYPE }}}')

    with pytest.raises(ValueError):
        render_json_template(template_file, **{"MUFFIN_TYPE": "banana"})


def test_render_json_template_invalid_json_missing_value(monkeypatch):
    template_file = StringIO.StringIO('{"type_of_muffin": {{ MUFFIN_TYPE }}}')

    with pytest.raises(ValueError):
        render_json_template(template_file, **{})
