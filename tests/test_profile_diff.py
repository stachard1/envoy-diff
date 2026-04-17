"""Tests for envoy_diff.profile_diff module."""

import pytest
from pathlib import Path
from envoy_diff.profile import save_profile
from envoy_diff.profile_diff import diff_profiles, report_profiles, ProfileDiffError


@pytest.fixture
def pdir(tmp_path):
    return tmp_path / "profiles"


ENV_A = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "8080", "NEW_KEY": "hello"}


def test_diff_profiles_detects_changes(pdir):
    save_profile("a", ENV_A, profile_dir=pdir)
    save_profile("b", ENV_B, profile_dir=pdir)
    result = diff_profiles("a", "b", profile_dir=pdir)
    assert "HOST" in result.changed


def test_diff_profiles_detects_added(pdir):
    save_profile("a", ENV_A, profile_dir=pdir)
    save_profile("b", ENV_B, profile_dir=pdir)
    result = diff_profiles("a", "b", profile_dir=pdir)
    assert "NEW_KEY" in result.added


def test_diff_profiles_detects_removed(pdir):
    save_profile("a", ENV_A, profile_dir=pdir)
    save_profile("b", ENV_B, profile_dir=pdir)
    result = diff_profiles("a", "b", profile_dir=pdir)
    assert "DEBUG" in result.removed


def test_diff_profiles_missing_a_raises(pdir):
    save_profile("b", ENV_B, profile_dir=pdir)
    with pytest.raises(ProfileDiffError, match="ghost"):
        diff_profiles("ghost", "b", profile_dir=pdir)


def test_diff_profiles_missing_b_raises(pdir):
    save_profile("a", ENV_A, profile_dir=pdir)
    with pytest.raises(ProfileDiffError, match="ghost"):
        diff_profiles("a", "ghost", profile_dir=pdir)


def test_report_profiles_returns_report(pdir):
    save_profile("a", ENV_A, profile_dir=pdir)
    save_profile("b", ENV_B, profile_dir=pdir)
    report = report_profiles("a", "b", profile_dir=pdir)
    assert report is not None
    assert hasattr(report, "diff")
    assert hasattr(report, "audit")


def test_report_profiles_missing_raises(pdir):
    with pytest.raises(ProfileDiffError):
        report_profiles("x", "y", profile_dir=pdir)
