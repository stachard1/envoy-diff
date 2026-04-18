import pytest
from envoy_diff.linter import (
    lint_env, has_issues, errors, warnings, summary,
    LintResult, LintIssue
)

def test_valid_env_no_issues():
    result = lint_env({"APP_NAME": "myapp", "PORT": "8080"})
    assert not has_issues(result)

def test_lowercase_key_produces_warning():
    result = lint_env({"app_name": "myapp"})
    assert any(i.key == "app_name" and i.severity == "warning" for i in result.issues)

def test_lowercase_allowed_when_flag_set():
    result = lint_env({"app_name": "myapp"}, allow_lowercase=True)
    assert not has_issues(result)

def test_key_starting_with_digit_is_error():
    result = lint_env({"1BAD": "val"})
    assert any(i.key == "1BAD" and i.severity == "error" for i in result.issues)

def test_empty_value_is_warning():
    result = lint_env({"EMPTY_KEY": ""})
    assert any(i.key == "EMPTY_KEY" and "empty" in i.message.lower() for i in result.issues)

def test_leading_whitespace_is_warning():
    result = lint_env({"KEY": "  value"})
    assert any("whitespace" in i.message.lower() for i in result.issues)

def test_trailing_whitespace_is_warning():
    result = lint_env({"KEY": "value  "})
    assert any("whitespace" in i.message.lower() for i in result.issues)

def test_consecutive_spaces_is_warning():
    result = lint_env({"KEY": "hello  world"})
    assert any("consecutive" in i.message.lower() for i in result.issues)

def test_errors_filters_correctly():
    result = lint_env({"1BAD": "val", "good_key": "val"})
    assert all(i.severity == "error" for i in errors(result))

def test_warnings_filters_correctly():
    result = lint_env({"good_key": "val"})
    assert all(i.severity == "warning" for i in warnings(result))

def test_summary_format():
    result = lint_env({"1BAD": "", "good_key": ""})
    s = summary(result)
    assert "error" in s and "warning" in s

def test_empty_env_no_issues():
    result = lint_env({})
    assert not has_issues(result)
