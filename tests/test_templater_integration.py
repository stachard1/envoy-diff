"""Integration tests: templater combined with differ, auditor, and redactor."""

import pytest
from envoy_diff.templater import render_template
from envoy_diff.differ import diff_envs
from envoy_diff.auditor import audit_diff
from envoy_diff.redactor import redact_env


@pytest.fixture()
def before():
    return {
        "DB_HOST": "old-db.internal",
        "DB_PASSWORD": "old-secret",
        "APP_ENV": "staging",
    }


@pytest.fixture()
def template():
    return {
        "DB_HOST": "${NEW_DB_HOST}",
        "DB_PASSWORD": "${NEW_DB_PASSWORD}",
        "APP_ENV": "production",
    }


@pytest.fixture()
def context():
    return {
        "NEW_DB_HOST": "prod-db.internal",
        "NEW_DB_PASSWORD": "super-secret-prod",
    }


def test_render_then_diff_detects_changes(before, template, context):
    result = render_template(template, context)
    diff = diff_envs(before, result.rendered)
    assert diff.has_changes
    assert "DB_HOST" in diff.changed
    assert "APP_ENV" in diff.changed


def test_render_then_audit_flags_sensitive_password(before, template, context):
    result = render_template(template, context)
    diff = diff_envs(before, result.rendered)
    audit = audit_diff(diff)
    sensitive_keys = [f.key for f in audit.findings]
    assert "DB_PASSWORD" in sensitive_keys


def test_render_with_redacted_context_leaves_placeholders(before, template, context):
    redacted_ctx = redact_env(context)
    result = render_template(template, redacted_ctx)
    assert result.rendered["DB_PASSWORD"] == "***REDACTED***"
    assert result.substitutions == 2


def test_unresolved_vars_do_not_propagate_to_diff(before, template):
    # Render with empty context — vars stay as ${...}
    result = render_template(template, {})
    assert result.has_unresolved
    diff = diff_envs(before, result.rendered)
    # All keys changed because placeholders differ from real values
    assert diff.has_changes
