"""Tests for envoy_diff.baseline."""

import json
import os
import pytest

from envoy_diff.baseline import (
    establish_baseline,
    compare_to_baseline,
    update_baseline_if_clean,
)


ENV_A = {"HOST": "localhost", "PORT": "8080"}
ENV_B = {"HOST": "prod.example.com", "PORT": "8080", "DEBUG": "false"}


@pytest.fixture()
def snap_path(tmp_path):
    return str(tmp_path / "baseline.json")


def test_establish_baseline_creates_file(snap_path):
    establish_baseline(ENV_A, snap_path)
    assert os.path.exists(snap_path)


def test_establish_baseline_stores_env(snap_path):
    establish_baseline(ENV_A, snap_path)
    data = json.loads(open(snap_path).read())
    assert data["env"] == ENV_A


def test_compare_no_snapshot_shows_all_added(snap_path):
    result = compare_to_baseline(ENV_A, snap_path)
    assert result.baseline_existed is False
    assert set(result.diff.added.keys()) == set(ENV_A.keys())


def test_compare_with_snapshot_detects_changes(snap_path):
    establish_baseline(ENV_A, snap_path)
    result = compare_to_baseline(ENV_B, snap_path)
    assert result.baseline_existed is True
    assert "DEBUG" in result.diff.added
    assert "HOST" in result.diff.changed


def test_compare_identical_env_no_changes(snap_path):
    establish_baseline(ENV_A, snap_path)
    result = compare_to_baseline(ENV_A, snap_path)
    assert not result.diff.has_changes()


def test_update_baseline_if_clean_updates_when_no_changes(snap_path):
    establish_baseline(ENV_A, snap_path)
    updated = update_baseline_if_clean(ENV_A, snap_path)
    assert updated is True


def test_update_baseline_if_clean_skips_when_changes(snap_path):
    establish_baseline(ENV_A, snap_path)
    updated = update_baseline_if_clean(ENV_B, snap_path)
    assert updated is False


def test_update_baseline_force_overrides(snap_path):
    establish_baseline(ENV_A, snap_path)
    updated = update_baseline_if_clean(ENV_B, snap_path, force=True)
    assert updated is True
    data = json.loads(open(snap_path).read())
    assert data["env"] == ENV_B


def test_snapshot_path_stored_in_result(snap_path):
    result = compare_to_baseline(ENV_A, snap_path)
    assert result.snapshot_path == snap_path
