"""Tests for envoy_diff.validator."""

import pytest
from envoy_diff.validator import validate_env, ValidationIssue


def test_valid_env_no_issues():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = validate_env(env)
    assert not result.has_issues


def test_blank_value_produces_warning():
    env = {"HOST": ""}
    result = validate_env(env)
    assert result.has_issues
    assert any(i.key == "HOST" and i.severity == "warning" for i in result.issues)


def test_blank_value_allowed_when_disabled():
    env = {"HOST": ""}
    result = validate_env(env, disallow_blank=False)
    assert not result.has_issues


def test_invalid_key_characters_produce_error():
    env = {"BAD-KEY": "value"}
    result = validate_env(env)
    assert any(i.key == "BAD-KEY" and i.severity == "error" for i in result.issues)


def test_missing_required_key_produces_error():
    env = {"HOST": "localhost"}
    result = validate_env(env, required_keys=["PORT"])
    assert any(i.key == "PORT" and i.severity == "error" for i in result.issues)


def test_present_required_key_no_error():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = validate_env(env, required_keys=["HOST", "PORT"])
    assert not result.errors


def test_summary_no_issues():
    result = validate_env({"A": "1"})
    assert result.summary() == "All variables passed validation."


def test_summary_with_issues():
    env = {"BAD-KEY": "", "GOOD": ""}
    result = validate_env(env, required_keys=["MISSING"])
    assert "error" in result.summary()
    assert "warning" in result.summary()


def test_errors_and_warnings_split():
    env = {"BAD-KEY": "ok", "EMPTY": ""}
    result = validate_env(env)
    assert len(result.errors) >= 1
    assert len(result.warnings) >= 1


def test_empty_env_no_issues():
    result = validate_env({})
    assert not result.has_issues
