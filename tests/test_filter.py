"""Tests for envoy_diff.filter."""
import pytest
from envoy_diff.filter import filter_by_prefix, filter_by_pattern, filter_by_tag, filter_env


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "APP_PORT": "8080",
        "APP_DEBUG": "true",
        "SECRET_KEY": "abc123",
        "LOG_LEVEL": "info",
    }


def test_filter_by_prefix_matches(env):
    r = filter_by_prefix(env, "DB")
    assert "DB_HOST" in r.matched
    assert "DB_PASSWORD" in r.matched
    assert "APP_PORT" not in r.matched


def test_filter_by_prefix_excluded(env):
    r = filter_by_prefix(env, "DB")
    assert "APP_PORT" in r.excluded


def test_filter_by_prefix_empty_result(env):
    r = filter_by_prefix(env, "XYZ")
    assert r.count == 0


def test_filter_by_pattern_matches(env):
    r = filter_by_pattern(env, r"PASSWORD|SECRET")
    assert "DB_PASSWORD" in r.matched
    assert "SECRET_KEY" in r.matched


def test_filter_by_pattern_no_match(env):
    r = filter_by_pattern(env, r"NONEXISTENT")
    assert r.count == 0


def test_filter_by_tag_sensitive(env):
    r = filter_by_tag(env, "sensitive")
    assert "DB_PASSWORD" in r.matched
    assert "SECRET_KEY" in r.matched
    assert "APP_PORT" not in r.matched


def test_filter_by_tag_excludes_others(env):
    r = filter_by_tag(env, "sensitive")
    assert "LOG_LEVEL" in r.excluded


def test_filter_env_prefix_and_tag(env):
    r = filter_env(env, prefix="DB", tag="sensitive")
    assert "DB_PASSWORD" in r.matched
    assert "DB_HOST" not in r.matched


def test_filter_env_no_filters(env):
    r = filter_env(env)
    assert r.matched == env
    assert r.excluded == {}


def test_filter_env_count(env):
    r = filter_by_prefix(env, "APP")
    assert r.count == 2
