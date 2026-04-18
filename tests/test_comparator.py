import pytest
from unittest.mock import patch
from envoy_diff.comparator import compare_profiles, compare_snapshots, CompareResult


ENV_A = {"HOST": "localhost", "PORT": "8080", "SECRET_KEY": "old"}
ENV_B = {"HOST": "prod.example.com", "PORT": "8080", "SECRET_KEY": "new", "DEBUG": "true"}


@patch("envoy_diff.comparator.load_profile")
def test_compare_profiles_returns_result(mock_load):
    mock_load.side_effect = lambda name, d: ENV_A if name == "staging" else ENV_B
    result = compare_profiles("staging", "prod")
    assert isinstance(result, CompareResult)
    assert result.label_a == "staging"
    assert result.label_b == "prod"


@patch("envoy_diff.comparator.load_profile")
def test_compare_profiles_detects_changes(mock_load):
    mock_load.side_effect = lambda name, d: ENV_A if name == "staging" else ENV_B
    result = compare_profiles("staging", "prod")
    assert result.diff.has_changes()
    assert "HOST" in result.diff.changed
    assert "DEBUG" in result.diff.added


@patch("envoy_diff.comparator.load_profile")
def test_compare_profiles_audit_flags_sensitive(mock_load):
    mock_load.side_effect = lambda name, d: ENV_A if name == "staging" else ENV_B
    result = compare_profiles("staging", "prod")
    sensitive_keys = [f.key for f in result.audit.findings]
    assert "SECRET_KEY" in sensitive_keys


@patch("envoy_diff.comparator.load_profile")
def test_compare_profiles_score_nonzero(mock_load):
    mock_load.side_effect = lambda name, d: ENV_A if name == "staging" else ENV_B
    result = compare_profiles("staging", "prod")
    assert result.score.total > 0


@patch("envoy_diff.comparator.load_profile")
def test_compare_profiles_summary_contains_labels(mock_load):
    mock_load.side_effect = lambda name, d: ENV_A if name == "staging" else ENV_B
    result = compare_profiles("staging", "prod")
    s = result.summary()
    assert "staging" in s
    assert "prod" in s
    assert "Risk" in s


@patch("envoy_diff.comparator.load_snapshot")
def test_compare_snapshots_returns_result(mock_load):
    mock_load.side_effect = lambda path: ENV_A if "a" in path else ENV_B
    result = compare_snapshots("snap_a.json", "snap_b.json")
    assert isinstance(result, CompareResult)


@patch("envoy_diff.comparator.load_snapshot")
def test_compare_snapshots_no_changes(mock_load):
    mock_load.return_value = ENV_A
    result = compare_snapshots("snap_a.json", "snap_b.json")
    assert not result.diff.has_changes()
    assert result.score.total == 0


@patch("envoy_diff.comparator.load_profile")
def test_compare_profiles_missing_profile_treated_as_empty(mock_load):
    mock_load.return_value = None
    result = compare_profiles("missing_a", "missing_b")
    assert not result.diff.has_changes()
