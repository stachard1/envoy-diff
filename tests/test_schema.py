"""Tests for envoy_diff.schema."""

import pytest
from envoy_diff.schema import SchemaRule, validate_schema


ENV = {
    "PORT": "8080",
    "ENV": "production",
    "LOG_LEVEL": "debug",
    "APP_NAME": "myapp",
}


def test_no_violations_when_env_matches_schema():
    rules = [
        SchemaRule(key="PORT", pattern=r"\d+", required=True),
        SchemaRule(key="ENV", allowed_values=["production", "staging", "dev"]),
    ]
    result = validate_schema(ENV, rules)
    assert not result.has_violations


def test_missing_required_key_is_error():
    rules = [SchemaRule(key="DATABASE_URL", required=True)]
    result = validate_schema(ENV, rules)
    assert result.has_violations
    assert any(v.key == "DATABASE_URL" for v in result.errors)


def test_missing_optional_key_no_violation():
    rules = [SchemaRule(key="OPTIONAL_KEY", required=False)]
    result = validate_schema(ENV, rules)
    assert not result.has_violations


def test_pattern_mismatch_is_warning():
    rules = [SchemaRule(key="PORT", pattern=r"[a-z]+")]
    result = validate_schema(ENV, rules)
    assert result.has_violations
    assert any(v.key == "PORT" and v.severity == "warning" for v in result.violations)


def test_allowed_values_violation_is_error():
    rules = [SchemaRule(key="LOG_LEVEL", allowed_values=["info", "warn", "error"])]
    result = validate_schema(ENV, rules)
    assert result.has_violations
    assert any(v.key == "LOG_LEVEL" and v.severity == "error" for v in result.errors)


def test_allowed_values_pass():
    rules = [SchemaRule(key="ENV", allowed_values=["production", "staging"])]
    result = validate_schema(ENV, rules)
    assert not result.has_violations


def test_summary_no_violations():
    result = validate_schema(ENV, [])
    assert "OK" in result.summary()


def test_summary_with_violations():
    rules = [
        SchemaRule(key="MISSING", required=True),
        SchemaRule(key="PORT", pattern=r"[a-z]+"),
    ]
    result = validate_schema(ENV, rules)
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_errors_and_warnings_properties():
    rules = [
        SchemaRule(key="MISSING", required=True),
        SchemaRule(key="PORT", pattern=r"[a-z]+"),
    ]
    result = validate_schema(ENV, rules)
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
