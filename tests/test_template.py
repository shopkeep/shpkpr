# third-party imports
import pytest

# local imports
from shpkpr.template import InvalidJSONError
from shpkpr.template import MissingTemplateError
from shpkpr.template import UndefinedError
from shpkpr.template import load_values_from_environment
from shpkpr.template import render_json_template
from shpkpr.template_filters import IntegerRequired
from shpkpr.template_filters import IntegerTooLarge
from shpkpr.template_filters import IntegerTooSmall
from shpkpr.template_filters import FloatRequired
from shpkpr.template_filters import FloatTooLarge
from shpkpr.template_filters import FloatTooSmall


def _write_template_to_disk(tmpdir, template_name, template_data):
    """shpkpr loads template files from disk normally. This convenience
    function writes a template file to disk and returns a (directory, name)
    tuple.
    """
    with tmpdir.join(template_name).open("w") as f:
        f.write(template_data)
    return (tmpdir.strpath, template_name)


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


def test_render_json_template_valid(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"type_of_muffin": "{{ MUFFIN_TYPE }}"}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_TYPE": "banana"})
    assert "type_of_muffin" in rendered_template
    assert rendered_template["type_of_muffin"] == "banana"


def test_render_json_template_invalid_json_unquoted_string(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"type_of_muffin": {{ MUFFIN_TYPE }}}',
    )

    with pytest.raises(InvalidJSONError):
        render_json_template(template_path, template_name, **{"MUFFIN_TYPE": "banana"})


def test_render_json_template_invalid_json_missing_value(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"type_of_muffin": {{ MUFFIN_TYPE }}}',
    )

    with pytest.raises(InvalidJSONError):
        render_json_template(template_path, template_name, **{"MUFFIN_TYPE": ""})


def test_render_json_template_missing_value_raises(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"type_of_muffin": "{{ MUFFIN_TYPE }}"}',
    )

    with pytest.raises(UndefinedError):
        render_json_template(template_path, template_name, **{})


def test_render_json_template_all_env(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '''
        {
            "types_of_muffin": {
                {% for k, v in _all_env|filter_items("MUFFIN_", True) %}
                "{{ k.lower() }}": {{ v }}{% if loop.last == False %},{% endif %}
                {% endfor %}
            }
        }
        ''',
    )

    rendered_template = render_json_template(template_path, template_name, **{
        "MUFFIN_BLUEBERRY": 4,
        "MUFFIN_BANANA": 7,
        "MUFFIN_CHOCOLATE": 12,
        "DONUT_STRAWBERRY": 9,
    })
    assert "types_of_muffin" in rendered_template
    assert rendered_template["types_of_muffin"]["blueberry"] == 4
    assert rendered_template["types_of_muffin"]["banana"] == 7
    assert rendered_template["types_of_muffin"]["chocolate"] == 12


def test_render_json_template_require_int(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_int }}}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "1"})
    assert rendered_template['muffin_count'] == 1


def test_render_json_template_require_int_requires_int(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_int }}}',
    )

    with pytest.raises(IntegerRequired):
        render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "one muffin"})


def test_render_json_template_require_int_min_constraint(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_int(min=50) }}}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "60"})
    assert rendered_template['muffin_count'] == 60


def test_render_json_template_require_int_min_constraint_raises(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_int(min=50) }}}',
    )

    with pytest.raises(IntegerTooSmall):
        render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "40"})


def test_render_json_template_require_int_max_constraint(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_int(max=50) }}}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "-60"})
    assert rendered_template['muffin_count'] == -60


def test_render_json_template_require_int_max_constraint_raises(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_int(max=50) }}}',
    )

    with pytest.raises(IntegerTooLarge):
        render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "60"})


def test_render_json_template_require_float(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_float }}}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "1.01"})
    assert rendered_template['muffin_count'] == 1.01


def test_render_json_template_require_float_requires_float(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_float }}}',
    )

    with pytest.raises(FloatRequired):
        render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "one muffin"})


def test_render_json_template_require_float_min_constraint(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_float(min=50) }}}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "60"})
    assert rendered_template['muffin_count'] == 60


def test_render_json_template_require_float_min_constraint_raises(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_float(min=50) }}}',
    )

    with pytest.raises(FloatTooSmall):
        render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "40"})


def test_render_json_template_require_float_max_constraint(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_float(max=50) }}}',
    )

    rendered_template = render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "-60"})
    assert rendered_template['muffin_count'] == -60


def test_render_json_template_require_float_max_constraint_raises(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '{"muffin_count": {{ MUFFIN_COUNT|require_float(max=50) }}}',
    )

    with pytest.raises(FloatTooLarge):
        render_json_template(template_path, template_name, **{"MUFFIN_COUNT": "60"})


def test_render_json_template_with_inheritance_valid(tmpdir):
    _write_template_to_disk(
        tmpdir.mkdir('bases'), 'base.json',
        '{"type_of_muffin": "{% block MUFFIN_TYPE_PLACEHOLDER %}{{ MUFFIN_TYPE }}{% endblock %}"}',
    )
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '''
        {% extends "bases/base.json" %}
        {% block MUFFIN_TYPE_PLACEHOLDER %}{{ ALT_MUFFIN_TYPE }}{% endblock %}
        ''',
    )

    rendered_template = render_json_template(template_path, template_name, **{
        "MUFFIN_TYPE": "banana",
        "ALT_MUFFIN_TYPE": "blueberry",
    })
    assert "type_of_muffin" in rendered_template
    assert rendered_template["type_of_muffin"] == "blueberry"


def test_render_json_template_with_inheritance_no_parent(tmpdir):
    template_path, template_name = _write_template_to_disk(
        tmpdir, 'template.json',
        '''
        {% extends "bases/base.json" %}
        {% block MUFFIN_TYPE_PLACEHOLDER %}{{ ALT_MUFFIN_TYPE }}{% endblock %}
        ''',
    )

    with pytest.raises(MissingTemplateError):
        render_json_template(template_path, template_name, **{})
