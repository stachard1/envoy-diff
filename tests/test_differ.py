"""Tests for envoy_diff.differ module."""

import pytest
from envoy_diff.differ import diff_envs, EnvDiffResult


BEFORE = {
    "APP_ENV": "staging",
    "DB_HOST": "localhost",
    "SECRET_KEY": "old-secret",
    "DEPRECATED": "yes",
}

AFTER = {
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "SECRET_KEY": "new-secret",
    "NEW_FEATURE": "enabled",
}


def test_added_keys():
    result = diff_envs(BEFORE, AFTER)
    assert "NEW_FEATURE" in result.added
    assert result.added["NEW_FEATURE"] == "enabled"


def test_removed_keys():
    result = diff_envs(BEFORE, AFTER)
    assert "DEPRECATED" in result.removed
    assert result.removed["DEPRECATED"] == "yes"


def test_changed_keys():
    result = diff_envs(BEFORE, AFTER)
    assert "APP_ENV" in result.changed
    assert result.changed["APP_ENV"] == ("staging", "production")
    assert "SECRET_KEY" in result.changed


def test_unchanged_keys():
    result = diff_envs(BEFORE, AFTER)
    assert "DB_HOST" in result.unchanged
    assert result.unchanged["DB_HOST"] == "localhost"


def test_no_changes():
    result = diff_envs(BEFORE, BEFORE)
    assert not result.has_changes
    assert result.summary() == "No changes detected."


def test_has_changes():
    result = diff_envs(BEFORE, AFTER)
    assert result.has_changes


def test_summary_string():
    result = diff_envs(BEFORE, AFTER)
    summary = result.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary


def test_ignore_keys():
    result = diff_envs(BEFORE, AFTER, ignore_keys=["SECRET_KEY", "NEW_FEATURE"])
    assert "SECRET_KEY" not in result.changed
    assert "NEW_FEATURE" not in result.added


def test_empty_envs():
    result = diff_envs({}, {})
    assert not result.has_changes


def test_all_added():
    result = diff_envs({}, {"FOO": "bar"})
    assert "FOO" in result.added
    assert not result.removed
    assert not result.changed
