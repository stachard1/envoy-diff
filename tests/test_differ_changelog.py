"""Tests for differ_changelog and changelog_cli."""
from __future__ import annotations

import json
import os
import pytest

from envoy_diff.differ_changelog import build_changelog, ChangelogEntry, Changelog


BEFORE = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_PASS": "secret"}
AFTER = {"APP_HOST": "prod.example.com", "APP_PORT": "8080", "NEW_KEY": "value"}
IDENTICAL = dict(BEFORE)


@pytest.fixture
def changelog():
    snapshots = [
        ("v1->v2", BEFORE, AFTER),
        ("v2->v2", AFTER, AFTER),
    ]
    return build_changelog(snapshots, timestamp="2024-01-01T00:00:00")


def test_build_changelog_returns_changelog(changelog):
    assert isinstance(changelog, Changelog)


def test_changelog_has_correct_entry_count(changelog):
    assert changelog.total_entries == 2


def test_first_entry_has_changes(changelog):
    assert changelog.entries[0].has_changes is True


def test_second_entry_no_changes(changelog):
    assert changelog.entries[1].has_changes is False


def test_entry_label_preserved(changelog):
    assert changelog.entries[0].label == "v1->v2"


def test_entry_timestamp_preserved(changelog):
    assert changelog.entries[0].timestamp == "2024-01-01T00:00:00"


def test_sensitive_key_detected(changelog):
    entry = changelog.entries[0]
    assert any("PASS" in k or "pass" in k.lower() for k in entry.sensitive_keys)


def test_risk_level_is_string(changelog):
    assert isinstance(changelog.entries[0].risk_level, str)
    assert changelog.entries[0].risk_level in ("none", "low", "medium", "high", "critical")


def test_entries_with_changes_filters_correctly(changelog):
    changed = changelog.entries_with_changes()
    assert len(changed) == 1
    assert changed[0].label == "v1->v2"


def test_changelog_summary_contains_counts(changelog):
    s = changelog.summary()
    assert "2 entries" in s
    assert "1 with changes" in s


def test_entry_summary_contains_label(changelog):
    s = changelog.entries[0].summary()
    assert "v1->v2" in s


def test_entry_summary_shows_added_removed(changelog):
    s = changelog.entries[0].summary()
    assert "+" in s or "-" in s or "~" in s


def test_no_changes_entry_summary(changelog):
    s = changelog.entries[1].summary()
    assert "no changes" in s


def test_high_risk_entries_empty_when_low_risk():
    snapshots = [("safe", {"FOO": "bar"}, {"FOO": "bar"})]
    cl = build_changelog(snapshots)
    assert cl.high_risk_entries() == []
