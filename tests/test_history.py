"""Tests for envoy_diff.history module."""
import pytest
from pathlib import Path

from envoy_diff.history import (
    record_snapshot,
    list_history,
    load_history_entry,
    get_latest,
    purge_history,
)


@pytest.fixture
def hdir(tmp_path):
    return str(tmp_path / "history")


ENV_A = {"APP": "1", "DB": "postgres"}
ENV_B = {"APP": "2", "DB": "postgres", "NEW": "val"}


def test_record_snapshot_creates_file(hdir):
    path = record_snapshot(ENV_A, "prod", hdir)
    assert Path(path).exists()


def test_record_snapshot_appears_in_list(hdir):
    record_snapshot(ENV_A, "prod", hdir)
    history = list_history(hdir)
    assert len(history) == 1
    assert history[0]["label"] == "prod"


def test_multiple_snapshots_listed(hdir):
    record_snapshot(ENV_A, "prod", hdir)
    record_snapshot(ENV_B, "prod", hdir)
    history = list_history(hdir)
    assert len(history) == 2


def test_list_history_sorted_descending(hdir):
    record_snapshot(ENV_A, "prod", hdir)
    record_snapshot(ENV_B, "prod", hdir)
    history = list_history(hdir)
    assert history[0]["timestamp"] >= history[1]["timestamp"]


def test_load_history_entry_returns_env(hdir):
    record_snapshot(ENV_A, "staging", hdir)
    entry = list_history(hdir)[0]
    env = load_history_entry(entry)
    assert env == ENV_A


def test_get_latest_returns_most_recent(hdir):
    record_snapshot(ENV_A, "prod", hdir)
    record_snapshot(ENV_B, "prod", hdir)
    latest = get_latest("prod", hdir)
    assert latest is not None
    env = load_history_entry(latest)
    assert env == ENV_B


def test_get_latest_unknown_label_returns_none(hdir):
    record_snapshot(ENV_A, "prod", hdir)
    assert get_latest("staging", hdir) is None


def test_purge_removes_all(hdir):
    record_snapshot(ENV_A, "prod", hdir)
    record_snapshot(ENV_B, "prod", hdir)
    removed = purge_history(hdir)
    assert removed == 2
    assert list_history(hdir) == []


def test_purge_removes_snapshot_files(hdir):
    path = record_snapshot(ENV_A, "prod", hdir)
    purge_history(hdir)
    assert not Path(path).exists()


def test_empty_history_returns_empty_list(hdir):
    assert list_history(hdir) == []
