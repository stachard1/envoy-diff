"""Tests for envoy_diff.auditor module."""

import pytest
from envoy_diff.differ import EnvDiffResult
from envoy_diff.auditor import audit_diff, is_sensitive, AuditResult


# --- is_sensitive ---

def test_is_sensitive_secret():
    assert is_sensitive("DB_SECRET") is True

def test_is_sensitive_password():
    assert is_sensitive("MYSQL_PASSWORD") is True

def test_is_sensitive_token():
    assert is_sensitive("GITHUB_TOKEN") is True

def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True

def test_is_sensitive_auth():
    assert is_sensitive("AUTH_HEADER") is True

def test_not_sensitive_plain_key():
    assert is_sensitive("APP_PORT") is False

def test_not_sensitive_env():
    assert is_sensitive("ENVIRONMENT") is False


# --- audit_diff ---

def _make_result(added=None, removed=None, changed=None, unchanged=None):
    return EnvDiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


def test_audit_no_sensitive_changes():
    result = _make_result(added={"APP_PORT": "8080"}, changed={"LOG_LEVEL": ("info", "debug")})
    audit = audit_diff(result)
    assert not audit.has_findings


def test_audit_sensitive_added():
    result = _make_result(added={"DB_PASSWORD": "secret123"})
    audit = audit_diff(result)
    assert "DB_PASSWORD" in audit.sensitive_added
    assert audit.has_findings


def test_audit_sensitive_removed():
    result = _make_result(removed={"API_KEY": "old"})
    audit = audit_diff(result)
    assert "API_KEY" in audit.sensitive_removed


def test_audit_sensitive_changed():
    result = _make_result(changed={"GITHUB_TOKEN": ("old_token", "new_token")})
    audit = audit_diff(result)
    assert "GITHUB_TOKEN" in audit.sensitive_changed


def test_audit_summary_has_findings():
    result = _make_result(added={"AUTH_TOKEN": "xyz"})
    audit = audit_diff(result)
    summary = audit.summary()
    assert "AUTH_TOKEN" in summary
    assert "[AUDIT]" in summary


def test_audit_summary_no_findings():
    result = _make_result()
    audit = audit_diff(result)
    assert audit.summary() == "No sensitive key changes detected."
