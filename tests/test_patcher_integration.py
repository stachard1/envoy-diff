"""Integration tests: patcher combined with other modules."""

import pytest

from envoy_diff.patcher import patch_envs
from envoy_diff.auditor import audit_diff
from envoy_diff.differ import diff_envs
from envoy_diff.validator import validate_env
from envoy_diff.redactor import redact_env


@pytest.fixture
def base():
    return {"DB_HOST": "localhost", "DB_PASSWORD": "old_pass", "PORT": "5432"}


@pytest.fixture
def target():
    return {"DB_HOST": "prod.db", "DB_PASSWORD": "new_pass", "PORT": "5432", "API_KEY": "xyz"}


def test_patch_then_diff_shows_no_changes(base, target):
    """Patching base to target then diffing should yield no changes."""
    result = patch_envs(base, target)
    diff = diff_envs(result.patched, target)
    assert not diff.added
    assert not diff.removed
    assert not diff.changed


def test_patch_then_audit_flags_sensitive_additions(base, target):
    """Audit of diff between base and patched env should flag API_KEY."""
    result = patch_envs(base, target)
    diff = diff_envs(base, result.patched)
    audit = audit_diff(diff)
    sensitive_keys = {f.key for f in audit.findings}
    assert "API_KEY" in sensitive_keys or "DB_PASSWORD" in sensitive_keys


def test_patch_with_redacted_base(base, target):
    """Patch should still apply even when base was redacted."""
    redacted = redact_env(base)
    result = patch_envs(redacted, target)
    assert result.patched["DB_HOST"] == "prod.db"
    assert result.patched["API_KEY"] == "xyz"


def test_patch_skipping_sensitive_preserves_original_secret(base, target):
    """Skipping DB_PASSWORD keeps the original secret from base."""
    result = patch_envs(base, target, skip_keys=["DB_PASSWORD"])
    assert result.patched["DB_PASSWORD"] == "old_pass"
    assert "DB_PASSWORD" in result.skipped


def test_patch_result_passes_validation(base, target):
    """The patched env should pass basic validation."""
    result = patch_envs(base, target)
    vr = validate_env(result.patched)
    # No errors expected for well-formed keys
    assert not vr.errors()
