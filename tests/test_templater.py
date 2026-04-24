"""Tests for envoy_diff.templater."""

import pytest
from envoy_diff.templater import render_template, TemplateResult


def test_no_substitutions_returns_template_unchanged():
    tmpl = {"APP": "myapp", "PORT": "8080"}
    result = render_template(tmpl, {})
    assert result.rendered == tmpl
    assert result.substitutions == 0
    assert not result.has_unresolved


def test_dollar_brace_syntax_substituted():
    tmpl = {"DSN": "postgres://${DB_HOST}:5432/mydb"}
    ctx = {"DB_HOST": "localhost"}
    result = render_template(tmpl, ctx)
    assert result.rendered["DSN"] == "postgres://localhost:5432/mydb"
    assert result.substitutions == 1


def test_bare_dollar_syntax_substituted():
    tmpl = {"URL": "http://$HOST/api"}
    ctx = {"HOST": "example.com"}
    result = render_template(tmpl, ctx)
    assert result.rendered["URL"] == "http://example.com/api"
    assert result.substitutions == 1


def test_multiple_vars_in_one_value():
    tmpl = {"ADDR": "${PROTO}://${HOST}:${PORT}"}
    ctx = {"PROTO": "https", "HOST": "api.example.com", "PORT": "443"}
    result = render_template(tmpl, ctx)
    assert result.rendered["ADDR"] == "https://api.example.com:443"
    assert result.substitutions == 3


def test_unresolved_variable_tracked():
    tmpl = {"KEY": "${MISSING_VAR}"}
    result = render_template(tmpl, {})
    assert "MISSING_VAR" in result.unresolved
    assert result.has_unresolved
    assert result.rendered["KEY"] == "${MISSING_VAR}"  # left as-is


def test_strict_mode_raises_on_unresolved():
    tmpl = {"KEY": "${UNDEFINED}"}
    with pytest.raises(ValueError, match="UNDEFINED"):
        render_template(tmpl, {}, strict=True)


def test_strict_mode_passes_when_all_resolved():
    tmpl = {"KEY": "${DEFINED}"}
    result = render_template(tmpl, {"DEFINED": "value"}, strict=True)
    assert result.rendered["KEY"] == "value"


def test_context_defaults_to_empty():
    tmpl = {"PLAIN": "no-vars-here"}
    result = render_template(tmpl)
    assert result.rendered["PLAIN"] == "no-vars-here"


def test_duplicate_unresolved_deduplicated():
    tmpl = {"A": "${X}", "B": "${X}"}
    result = render_template(tmpl, {})
    assert result.unresolved.count("X") == 1


def test_summary_includes_substitution_count():
    tmpl = {"K": "${V}"}
    result = render_template(tmpl, {"V": "1"})
    assert "1 substitution" in result.summary()


def test_summary_includes_unresolved_when_present():
    tmpl = {"K": "${GHOST}"}
    result = render_template(tmpl, {})
    assert "GHOST" in result.summary()
    assert "unresolved" in result.summary()
