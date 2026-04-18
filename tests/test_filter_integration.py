"""Integration tests combining filter with differ and auditor."""
import pytest
from envoy_diff.filter import filter_env
from envoy_diff.differ import diff_envs
from envoy_diff.auditor import audit_diff


@pytest.fixture
def before():
    return {
        "DB_HOST": "db1.internal",
        "DB_PASSWORD": "old_pass",
        "APP_PORT": "8080",
        "LOG_LEVEL": "info",
    }


@pytest.fixture
def after():
    return {
        "DB_HOST": "db2.internal",
        "DB_PASSWORD": "new_pass",
        "APP_PORT": "8080",
        "LOG_LEVEL": "debug",
        "APP_DEBUG": "true",
    }


def test_filter_then_diff_only_db_keys(before, after):
    fb = filter_env(before, prefix="DB").matched
    fa = filter_env(after, prefix="DB").matched
    result = diff_envs(fb, fa)
    assert "DB_HOST" in result.changed
    assert "APP_PORT" not in result.changed
    assert "APP_DEBUG" not in result.added


def test_filter_sensitive_then_audit(before, after):
    fb = filter_env(before, tag="sensitive").matched
    fa = filter_env(after, tag="sensitive").matched
    diff = diff_envs(fb, fa)
    audit = audit_diff(diff)
    assert audit.has_findings()


def test_filter_pattern_limits_diff_scope(before, after):
    fb = filter_env(before, pattern=r"LOG").matched
    fa = filter_env(after, pattern=r"LOG").matched
    diff = diff_envs(fb, fa)
    assert "LOG_LEVEL" in diff.changed
    assert len(diff.added) == 0
    assert len(diff.removed) == 0
