import pytest
from envoy_diff.differ import diff_envs
from envoy_diff.scorer import score_diff, RiskScore, _level


def test_no_changes_score_is_zero():
    diff = diff_envs({"A": "1"}, {"A": "1"})
    result = score_diff(diff)
    assert result.total == 0
    assert result.level == "none"


def test_added_non_sensitive_contributes_low_weight():
    diff = diff_envs({}, {"APP_NAME": "myapp"})
    result = score_diff(diff)
    assert result.breakdown.get("added", 0) == 1
    assert result.level == "low"


def test_added_sensitive_key_higher_weight():
    diff = diff_envs({}, {"SECRET_KEY": "abc"})
    result = score_diff(diff)
    assert result.breakdown.get("added_sensitive", 0) == 3


def test_removed_key_contributes_weight():
    diff = diff_envs({"HOST": "localhost"}, {})
    result = score_diff(diff)
    assert result.breakdown.get("removed", 0) == 2


def test_changed_sensitive_key_highest_weight():
    diff = diff_envs({"DB_PASSWORD": "old"}, {"DB_PASSWORD": "new"})
    result = score_diff(diff)
    assert result.breakdown.get("changed_sensitive", 0) == 4


def test_level_medium_threshold():
    diff = diff_envs(
        {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        {},
    )
    result = score_diff(diff)
    assert result.total == 10
    assert result.level == "medium"


def test_level_high_threshold():
    diff = diff_envs(
        {"API_TOKEN": "x", "SECRET": "y", "AUTH_KEY": "z"},
        {},
    )
    result = score_diff(diff)
    assert result.level == "high"


def test_level_helper():
    assert _level(0) == "none"
    assert _level(3) == "low"
    assert _level(10) == "medium"
    assert _level(20) == "high"


def test_score_returns_risk_score_instance():
    diff = diff_envs({"X": "1"}, {"X": "2"})
    result = score_diff(diff)
    assert isinstance(result, RiskScore)
