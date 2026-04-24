"""Tests for envoy_diff.differ_summary."""

import pytest
from envoy_diff.differ_summary import build_diff_summary, DiffSummary


@pytest.fixture
def clean_envs():
    a = {"APP_NAME": "myapp", "PORT": "8080", "LOG_LEVEL": "info"}
    b = {"APP_NAME": "myapp", "PORT": "9090", "LOG_LEVEL": "info"}
    return a, b


@pytest.fixture
def sensitive_envs():
    a = {"APP_NAME": "myapp", "DB_PASSWORD": "old_secret"}
    b = {"APP_NAME": "myapp", "DB_PASSWORD": "new_secret", "API_TOKEN": "tok123"}
    return a, b


@pytest.fixture
def identical_envs():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    return env, dict(env)


def test_build_diff_summary_returns_diff_summary(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    assert isinstance(result, DiffSummary)


def test_has_changes_when_envs_differ(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    assert result.has_changes is True


def test_no_changes_when_identical(identical_envs):
    a, b = identical_envs
    result = build_diff_summary(a, b)
    assert result.has_changes is False


def test_labels_stored_correctly(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b, label_a="prod", label_b="staging")
    assert result.label_a == "prod"
    assert result.label_b == "staging"


def test_default_labels(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    assert result.label_a == "before"
    assert result.label_b == "after"


def test_has_findings_for_sensitive_change(sensitive_envs):
    a, b = sensitive_envs
    result = build_diff_summary(a, b)
    assert result.has_findings is True


def test_no_findings_for_clean_change(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    assert result.has_findings is False


def test_risk_level_is_string(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    assert isinstance(result.risk_level, str)
    assert result.risk_level in ("none", "low", "medium", "high", "critical")


def test_summary_contains_labels(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b, label_a="v1", label_b="v2")
    text = result.summary()
    assert "v1" in text
    assert "v2" in text


def test_summary_contains_risk(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    assert "Risk" in result.summary()


def test_as_dict_structure(sensitive_envs):
    a, b = sensitive_envs
    result = build_diff_summary(a, b)
    d = result.as_dict()
    assert "label_a" in d
    assert "label_b" in d
    assert "changes" in d
    assert "risk" in d
    assert "findings" in d
    assert "sensitive_changes" in d


def test_as_dict_findings_are_sensitive_keys(sensitive_envs):
    a, b = sensitive_envs
    result = build_diff_summary(a, b)
    d = result.as_dict()
    for key in d["findings"]:
        assert any(s in key.lower() for s in ("password", "token", "secret", "key", "auth"))


def test_as_dict_changed_key_present(clean_envs):
    a, b = clean_envs
    result = build_diff_summary(a, b)
    d = result.as_dict()
    assert "PORT" in d["changes"]["changed"]
