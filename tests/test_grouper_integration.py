"""Integration tests combining grouper with differ output."""
import pytest
from envoy_diff.differ import diff_envs
from envoy_diff.grouper import group_by_prefix, group_by_tag, group_summary


@pytest.fixture
def before():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_ENV": "staging",
        "SECRET_TOKEN": "old",
    }


@pytest.fixture
def after():
    return {
        "DB_HOST": "prod-db",
        "DB_PORT": "5432",
        "APP_ENV": "production",
        "SECRET_TOKEN": "new",
        "LOG_LEVEL": "warn",
    }


def test_group_added_keys_by_prefix(before, after):
    """Added keys should be groupable by prefix after diffing."""
    result = diff_envs(before, after)
    added_env = {k: after[k] for k in result.added}
    groups = group_by_prefix(added_env)
    assert "LOG" in groups


def test_group_changed_keys_by_prefix(before, after):
    """Changed keys should produce at least one recognisable prefix group."""
    result = diff_envs(before, after)
    changed_env = {k: after[k] for k in result.changed}
    groups = group_by_prefix(changed_env)
    assert "DB" in groups or "APP" in groups or "SECRET" in groups


def test_group_by_tag_flags_sensitive(before, after):
    """SECRET_TOKEN should appear in tag-based groups for changed keys."""
    result = diff_envs(before, after)
    changed_env = {k: after[k] for k in result.changed}
    groups = group_by_tag(changed_env)
    all_keys = [k for g in groups.values() for k in g.keys]
    assert "SECRET_TOKEN" in all_keys


def test_group_summary_non_empty(before, after):
    """group_summary should return a non-empty string containing '->'."""
    groups = group_by_prefix(after)
    s = group_summary(groups)
    assert s != ""
    assert "->" in s


def test_removed_keys_not_in_after_groups(before, after):
    """Keys removed between environments should not appear in groups built from 'after'."""
    result = diff_envs(before, after)
    after_groups = group_by_prefix(after)
    all_after_keys = {k for g in after_groups.values() for k in g.keys}
    for removed_key in result.removed:
        assert removed_key not in all_after_keys
