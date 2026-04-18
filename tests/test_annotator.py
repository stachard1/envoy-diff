"""Tests for envoy_diff.annotator."""

import pytest
from envoy_diff.differ import diff_envs
from envoy_diff.annotator import annotate_diff, AnnotatedDiff


@pytest.fixture
def diff():
    old = {"DB_HOST": "localhost", "SECRET_KEY": "abc", "PORT": "8080"}
    new = {"DB_HOST": "prod-db", "SECRET_KEY": "abc", "API_TOKEN": "tok123"}
    return diff_envs(old, new)


def test_annotate_diff_returns_annotated_diff(diff):
    result = annotate_diff(diff)
    assert isinstance(result, AnnotatedDiff)


def test_added_key_change_type(diff):
    result = annotate_diff(diff)
    added = [e for e in result.entries if e.key == "API_TOKEN"]
    assert len(added) == 1
    assert added[0].change_type == "added"


def test_removed_key_change_type(diff):
    result = annotate_diff(diff)
    removed = [e for e in result.entries if e.key == "PORT"]
    assert len(removed) == 1
    assert removed[0].change_type == "removed"


def test_changed_key_change_type(diff):
    result = annotate_diff(diff)
    changed = [e for e in result.entries if e.key == "DB_HOST"]
    assert len(changed) == 1
    assert changed[0].change_type == "changed"
    assert changed[0].old_value == "localhost"
    assert changed[0].new_value == "prod-db"


def test_unchanged_key_change_type(diff):
    result = annotate_diff(diff)
    unchanged = [e for e in result.entries if e.key == "SECRET_KEY"]
    assert len(unchanged) == 1
    assert unchanged[0].change_type == "unchanged"


def test_sensitive_key_flagged(diff):
    result = annotate_diff(diff)
    token = next(e for e in result.entries if e.key == "API_TOKEN")
    assert token.sensitive is True


def test_non_sensitive_key_not_flagged(diff):
    result = annotate_diff(diff)
    port = next(e for e in result.entries if e.key == "PORT")
    assert port.sensitive is False


def test_risk_note_sensitive_added(diff):
    result = annotate_diff(diff)
    token = next(e for e in result.entries if e.key == "API_TOKEN")
    assert "sensitive" in token.risk_note


def test_risk_note_plain_removed(diff):
    result = annotate_diff(diff)
    port = next(e for e in result.entries if e.key == "PORT")
    assert port.risk_note == "key removed"


def test_sensitive_changes_excludes_unchanged(diff):
    result = annotate_diff(diff)
    sensitive = result.sensitive_changes()
    keys = [e.key for e in sensitive]
    assert "SECRET_KEY" not in keys


def test_summary_format(diff):
    result = annotate_diff(diff)
    s = result.summary()
    assert "change" in s
    assert "sensitive" in s


def test_entries_sorted_by_key(diff):
    result = annotate_diff(diff)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
