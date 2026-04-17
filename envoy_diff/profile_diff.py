"""Diff two named profiles and produce a report."""

from typing import Optional
from pathlib import Path

from envoy_diff.profile import load_profile, DEFAULT_PROFILE_DIR
from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.reporter import generate_report, Report


class ProfileDiffError(Exception):
    pass


def diff_profiles(
    name_a: str,
    name_b: str,
    profile_dir: Path = DEFAULT_PROFILE_DIR,
) -> EnvDiffResult:
    """Diff two profiles by name. Raises ProfileDiffError if either is missing."""
    env_a = load_profile(name_a, profile_dir=profile_dir)
    if env_a is None:
        raise ProfileDiffError(f"Profile not found: {name_a!r}")
    env_b = load_profile(name_b, profile_dir=profile_dir)
    if env_b is None:
        raise ProfileDiffError(f"Profile not found: {name_b!r}")
    return diff_envs(env_a, env_b)


def report_profiles(
    name_a: str,
    name_b: str,
    profile_dir: Path = DEFAULT_PROFILE_DIR,
) -> Report:
    """Generate a full audit report comparing two named profiles."""
    env_a = load_profile(name_a, profile_dir=profile_dir)
    if env_a is None:
        raise ProfileDiffError(f"Profile not found: {name_a!r}")
    env_b = load_profile(name_b, profile_dir=profile_dir)
    if env_b is None:
        raise ProfileDiffError(f"Profile not found: {name_b!r}")
    return generate_report(env_a, env_b)
