"""Integration: transform -> diff -> audit pipeline."""
import pytest
from envoy_diff.transformer import TransformRule, apply_transforms
from envoy_diff.differ import diff_envs
from envoy_diff.auditor import audit_diff


@pytest.fixture
def before():
    return {"DB_HOST": "old-host", "APP_ENV": "staging", "SECRET_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture
def after():
    return {"DB_HOST": "new-host", "APP_ENV": "production", "SECRET_KEY": "xyz789"}


def test_transform_then_diff_detects_changes(before, after):
    rules = [TransformRule(key_pattern="DEBUG", action="delete")]
    transformed_before = apply_transforms(before, rules).env
    diff = diff_envs(transformed_before, after)
    assert "DB_HOST" in diff.changed
    assert "DEBUG" not in diff.removed  # already deleted before diff


def test_transform_remap_reduces_diff_noise(before, after):
    rules = [TransformRule(key_pattern="APP_ENV", action="remap", value_map={"staging": "production"})]
    transformed_before = apply_transforms(before, rules).env
    diff = diff_envs(transformed_before, after)
    assert "APP_ENV" not in diff.changed


def test_transform_then_audit_flags_sensitive_changes(before, after):
    diff = diff_envs(before, after)
    audit = audit_diff(diff)
    sensitive_keys = [f.key for f in audit.findings]
    assert "SECRET_KEY" in sensitive_keys


def test_transform_delete_sensitive_removes_from_audit(before, after):
    rules = [TransformRule(key_pattern="SECRET_KEY", action="delete")]
    transformed_before = apply_transforms(before, rules).env
    transformed_after = apply_transforms(after, rules).env
    diff = diff_envs(transformed_before, transformed_after)
    audit = audit_diff(diff)
    sensitive_keys = [f.key for f in audit.findings]
    assert "SECRET_KEY" not in sensitive_keys
