"""Tests for envoy_diff.formatter."""
import io
import json
import pytest
from envoy_diff.differ import EnvDiffResult
from envoy_diff.formatter import format_text, format_json


def _result(added=None, removed=None, changed=None, unchanged=None):
    return EnvDiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


def test_no_changes_text():
    out = io.StringIO()
    format_text(_result(), use_color=False, out=out)
    assert out.getvalue() == "No changes detected.\n"


def test_added_key_text():
    out = io.StringIO()
    format_text(_result(added={"FOO": "bar"}), use_color=False, out=out)
    assert "+ FOO=bar" in out.getvalue()


def test_removed_key_text():
    out = io.StringIO()
    format_text(_result(removed={"OLD": "val"}), use_color=False, out=out)
    assert "- OLD=val" in out.getvalue()


def test_changed_key_text():
    out = io.StringIO()
    format_text(_result(changed={"X": ("1", "2")}), use_color=False, out=out)
    content = out.getvalue()
    assert "~ X=1" in content
    assert "~ X=2" in content


def test_color_codes_present():
    out = io.StringIO()
    format_text(_result(added={"A": "b"}), use_color=True, out=out)
    assert "\033[" in out.getvalue()


def test_format_json_no_changes():
    out = io.StringIO()
    format_json(_result(), out=out)
    data = json.loads(out.getvalue())
    assert data["added"] == {}
    assert data["removed"] == {}
    assert data["changed"] == {}


def test_format_json_with_changes():
    out = io.StringIO()
    format_json(_result(added={"NEW": "val"}, changed={"K": ("a", "b")}), out=out)
    data = json.loads(out.getvalue())
    assert data["added"] == {"NEW": "val"}
    assert data["changed"]["K"] == {"old": "a", "new": "b"}
    assert "summary" in data
