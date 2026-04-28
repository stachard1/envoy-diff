"""Tests for envoy_diff.differ_stats."""
import pytest
from envoy_diff.differ_stats import compute_stats, stats_as_dict, DiffStats


@pytest.fixture
def clean_envs():
    before = {"APP_HOST": "localhost", "APP_PORT": "8080", "LOG_LEVEL": "info"}
    after = {"APP_HOST": "localhost", "APP_PORT": "8080", "LOG_LEVEL": "info"}
    return before, after


@pytest.fixture
def changed_envs():
    before = {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "secret",
        "OLD_KEY": "gone",
    }
    after = {
        "APP_HOST": "prodhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "newsecret",
        "NEW_KEY": "arrived",
    }
    return before, after


def test_compute_stats_returns_diff_stats(clean_envs):
    before, after = clean_envs
    stats = compute_stats(before, after)
    assert isinstance(stats, DiffStats)


def test_no_changes_stats_are_zero(clean_envs):
    before, after = clean_envs
    stats = compute_stats(before, after)
    assert stats.added == 0
    assert stats.removed == 0
    assert stats.changed == 0
    assert stats.total_changes == 0
    assert not stats.has_changes


def test_unchanged_count_matches(clean_envs):
    before, after = clean_envs
    stats = compute_stats(before, after)
    assert stats.unchanged == 3


def test_added_removed_changed_counts(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    assert stats.added == 1
    assert stats.removed == 1
    assert stats.changed == 2  # APP_HOST and DB_PASSWORD
    assert stats.total_changes == 4
    assert stats.has_changes


def test_sensitive_changes_detected(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    assert stats.sensitive_changes >= 1


def test_risk_score_nonzero_for_sensitive_change(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    assert stats.risk_score > 0
    assert stats.risk_level != "none"


def test_tag_counts_populated(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    assert isinstance(stats.tag_counts, dict)
    assert len(stats.tag_counts) > 0


def test_top_changed_keys_limited(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after, top_n=2)
    assert len(stats.top_changed_keys) <= 2


def test_summary_is_string(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    s = stats.summary()
    assert isinstance(s, str)
    assert "added=" in s
    assert "risk=" in s


def test_stats_as_dict_keys(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    d = stats_as_dict(stats)
    expected_keys = {
        "added", "removed", "changed", "unchanged",
        "total_changes", "sensitive_changes",
        "risk_score", "risk_level", "tag_counts", "top_changed_keys",
    }
    assert expected_keys == set(d.keys())


def test_stats_as_dict_values_match(changed_envs):
    before, after = changed_envs
    stats = compute_stats(before, after)
    d = stats_as_dict(stats)
    assert d["added"] == stats.added
    assert d["removed"] == stats.removed
    assert d["risk_level"] == stats.risk_level
