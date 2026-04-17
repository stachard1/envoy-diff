"""Baseline comparison: compare current env against a saved snapshot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from envoy_diff.snapshot import load_snapshot, save_snapshot
from envoy_diff.differ import diff_envs, EnvDiffResult


@dataclass
class BaselineResult:
    snapshot_path: str
    diff: EnvDiffResult
    baseline_existed: bool


def establish_baseline(env: dict[str, str], path: str) -> None:
    """Save the current env as the baseline snapshot."""
    save_snapshot(env, path)


def compare_to_baseline(
    env: dict[str, str], path: str
) -> BaselineResult:
    """Compare *env* against the snapshot at *path*.

    If no snapshot exists yet the diff will show every key as added.
    """
    baseline_existed = os.path.exists(path)
    if baseline_existed:
        stored = load_snapshot(path)
        baseline_env: dict[str, str] = stored.get("env", {})
    else:
        baseline_env = {}

    result = diff_envs(baseline_env, env)
    return BaselineResult(
        snapshot_path=path,
        diff=result,
        baseline_existed=baseline_existed,
    )


def update_baseline_if_clean(
    env: dict[str, str], path: str, *, force: bool = False
) -> bool:
    """Update the baseline only when there are no changes (or *force* is set).

    Returns True when the baseline was updated.
    """
    result = compare_to_baseline(env, path)
    if force or not result.diff.has_changes():
        establish_baseline(env, path)
        return True
    return False
