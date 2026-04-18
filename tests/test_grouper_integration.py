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
    result = diff_envs(before, after)
    added_env = {k: after[k] for k in result.added}
    groups = group_by_prefix(added_env)
    assert "LOG" in groups


def test_group_changed_keys_by_prefix(before, after):
    result = diff_envs(before, after)
    changed_env = {k: after[k] for k in result.changed}
    groups = group_by_prefix(changed_env)
    assert "DB" in groups or "APP" in groups or "SECRET" in groups


def test_group_by_tag_flags_sensitive(before, after):
    result = diff_envs(before, after)
    changed_env = {k: after[k] for k in result.changed}
    groups = group_by_tag(changed_env)
    all_keys = [k for g in groups.values() for k in g.keys]
    assert "SECRET_TOKEN" in all_keys


def test_group_summary_non_empty(before, after):
    groups = group_by_prefix(after)
    s = group_summary(groups)
    assert s != ""
    assert "->" in s
