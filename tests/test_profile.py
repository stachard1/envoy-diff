"""Tests for envoy_diff.profile module."""

import pytest
from pathlib import Path
from envoy_diff.profile import (
    save_profile,
    load_profile,
    list_profiles,
    delete_profile,
    profile_exists,
)


@pytest.fixture
def profile_dir(tmp_path):
    return tmp_path / "profiles"


ENV = {"HOST": "localhost", "PORT": "8080"}


def test_save_profile_creates_file(profile_dir):
    path = save_profile("staging", ENV, profile_dir=profile_dir)
    assert path.exists()


def test_load_profile_returns_env(profile_dir):
    save_profile("staging", ENV, profile_dir=profile_dir)
    result = load_profile("staging", profile_dir=profile_dir)
    assert result == ENV


def test_load_profile_missing_returns_none(profile_dir):
    result = load_profile("nonexistent", profile_dir=profile_dir)
    assert result is None


def test_list_profiles_empty(profile_dir):
    assert list_profiles(profile_dir=profile_dir) == []


def test_list_profiles_returns_names(profile_dir):
    save_profile("alpha", ENV, profile_dir=profile_dir)
    save_profile("beta", ENV, profile_dir=profile_dir)
    names = list_profiles(profile_dir=profile_dir)
    assert "alpha" in names
    assert "beta" in names


def test_delete_profile_removes_file(profile_dir):
    save_profile("staging", ENV, profile_dir=profile_dir)
    result = delete_profile("staging", profile_dir=profile_dir)
    assert result is True
    assert not profile_exists("staging", profile_dir=profile_dir)


def test_delete_profile_missing_returns_false(profile_dir):
    result = delete_profile("ghost", profile_dir=profile_dir)
    assert result is False


def test_profile_exists_true(profile_dir):
    save_profile("prod", ENV, profile_dir=profile_dir)
    assert profile_exists("prod", profile_dir=profile_dir) is True


def test_profile_exists_false(profile_dir):
    assert profile_exists("prod", profile_dir=profile_dir) is False


def test_overwrite_profile(profile_dir):
    save_profile("staging", ENV, profile_dir=profile_dir)
    new_env = {"HOST": "remote"}
    save_profile("staging", new_env, profile_dir=profile_dir)
    result = load_profile("staging", profile_dir=profile_dir)
    assert result == new_env
