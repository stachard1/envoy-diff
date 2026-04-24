"""Tests for envoy_diff.differ_batch."""
import pytest
from envoy_diff.differ_batch import batch_diff, BatchDiffResult, BatchEntry


@pytest.fixture()
def clean_pair():
    before = {"APP_ENV": "staging", "PORT": "8080"}
    after = {"APP_ENV": "staging", "PORT": "8080"}
    return ("clean", before, after)


@pytest.fixture()
def changed_pair():
    before = {"APP_ENV": "staging", "PORT": "8080"}
    after = {"APP_ENV": "production", "PORT": "8080", "NEW_KEY": "value"}
    return ("changed", before, after)


@pytest.fixture()
def sensitive_pair():
    before = {"DB_PASSWORD": "old_pass"}
    after = {"DB_PASSWORD": "new_pass"}
    return ("sensitive", before, after)


def test_batch_diff_returns_batch_result(clean_pair):
    result = batch_diff([clean_pair])
    assert isinstance(result, BatchDiffResult)


def test_batch_diff_single_entry(clean_pair):
    result = batch_diff([clean_pair])
    assert result.total == 1
    assert isinstance(result.entries[0], BatchEntry)


def test_batch_diff_no_changes_for_identical(clean_pair):
    result = batch_diff([clean_pair])
    assert not result.entries[0].has_changes
    assert result.changed_count == 0


def test_batch_diff_detects_changes(changed_pair):
    result = batch_diff([changed_pair])
    assert result.entries[0].has_changes
    assert result.changed_count == 1


def test_batch_diff_flags_sensitive(sensitive_pair):
    result = batch_diff([sensitive_pair])
    assert result.entries[0].has_findings
    assert result.flagged_count == 1


def test_batch_diff_multiple_pairs(clean_pair, changed_pair, sensitive_pair):
    result = batch_diff([clean_pair, changed_pair, sensitive_pair])
    assert result.total == 3
    assert result.changed_count == 2
    assert result.flagged_count == 1


def test_batch_diff_max_score_zero_for_clean(clean_pair):
    result = batch_diff([clean_pair])
    assert result.max_score == 0.0


def test_batch_diff_max_score_nonzero_for_sensitive(sensitive_pair):
    result = batch_diff([sensitive_pair])
    assert result.max_score > 0


def test_batch_diff_max_score_across_entries(clean_pair, sensitive_pair):
    result = batch_diff([clean_pair, sensitive_pair])
    assert result.max_score == max(e.score.total for e in result.entries)


def test_batch_diff_summary_string(clean_pair, changed_pair):
    result = batch_diff([clean_pair, changed_pair])
    s = result.summary()
    assert "2 pair(s)" in s
    assert "1 with changes" in s


def test_batch_diff_empty_input():
    result = batch_diff([])
    assert result.total == 0
    assert result.max_score == 0.0
    assert "0 pair(s)" in result.summary()


def test_batch_entry_label(changed_pair):
    result = batch_diff([changed_pair])
    assert result.entries[0].label == "changed"
