"""Tests for envoy_diff.patcher."""

import pytest

from envoy_diff.differ import diff_envs
from envoy_diff.patcher import apply_patch, patch_envs, PatchResult


@pytest.fixture
def base():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


@pytest.fixture
def target():
    return {"HOST": "prod.db", "PORT": "5432", "NEW_KEY": "hello"}


def test_patch_envs_returns_patch_result(base, target):
    result = patch_envs(base, target)
    assert isinstance(result, PatchResult)


def test_patch_adds_new_key(base, target):
    result = patch_envs(base, target)
    assert result.patched["NEW_KEY"] == "hello"


def test_patch_removes_deleted_key(base, target):
    result = patch_envs(base, target)
    assert "DEBUG" not in result.patched


def test_patch_updates_changed_key(base, target):
    result = patch_envs(base, target)
    assert result.patched["HOST"] == "prod.db"


def test_patch_preserves_unchanged_key(base, target):
    result = patch_envs(base, target)
    assert result.patched["PORT"] == "5432"


def test_applied_lists_changed_keys(base, target):
    result = patch_envs(base, target)
    assert "HOST" in result.applied
    assert "NEW_KEY" in result.applied
    assert "DEBUG" in result.applied


def test_skip_key_not_applied(base, target):
    result = patch_envs(base, target, skip_keys=["HOST"])
    assert result.patched["HOST"] == "localhost"
    assert "HOST" in result.skipped


def test_skip_removal_preserves_key(base, target):
    result = patch_envs(base, target, skip_keys=["DEBUG"])
    assert result.patched["DEBUG"] == "false"
    assert "DEBUG" in result.skipped


def test_has_skipped_false_when_none(base, target):
    result = patch_envs(base, target)
    assert not result.has_skipped


def test_has_skipped_true_when_some(base, target):
    result = patch_envs(base, target, skip_keys=["PORT"])
    assert result.has_skipped


def test_summary_contains_counts(base, target):
    result = patch_envs(base, target, skip_keys=["HOST"])
    s = result.summary()
    assert "applied=" in s
    assert "skipped=" in s


def test_apply_patch_directly(base, target):
    diff = diff_envs(base, target)
    result = apply_patch(base, diff)
    assert result.patched == patch_envs(base, target).patched


def test_empty_base_gets_all_target_keys():
    result = patch_envs({}, {"A": "1", "B": "2"})
    assert result.patched == {"A": "1", "B": "2"}


def test_identical_envs_produce_no_changes(base):
    result = patch_envs(base, base)
    assert result.patched == base
    assert result.applied == []
