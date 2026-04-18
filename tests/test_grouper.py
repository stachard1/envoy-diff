import pytest
from envoy_diff.grouper import group_by_prefix, group_by_tag, group_summary, EnvGroup


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envoy",
        "APP_ENV": "prod",
        "SECRET_KEY": "abc123",
        "LOG_LEVEL": "info",
    }


def test_group_by_prefix_returns_groups(sample_env):
    groups = group_by_prefix(sample_env)
    assert "DB" in groups
    assert "APP" in groups


def test_group_by_prefix_correct_keys(sample_env):
    groups = group_by_prefix(sample_env)
    assert set(groups["DB"].keys) == {"DB_HOST", "DB_PORT"}
    assert set(groups["APP"].keys) == {"APP_NAME", "APP_ENV"}


def test_group_by_prefix_single_key():
    env = {"ONLY_ONE": "value"}
    groups = group_by_prefix(env)
    assert "ONLY" in groups
    assert groups["ONLY"].keys == ["ONLY_ONE"]


def test_group_by_prefix_empty():
    assert group_by_prefix({}) == {}


def test_group_by_tag_sensitive(sample_env):
    groups = group_by_tag(sample_env)
    assert "sensitive" in groups
    assert "SECRET_KEY" in groups["sensitive"].keys


def test_group_by_tag_other_for_untagged():
    env = {"RANDOM_VAR": "x"}
    groups = group_by_tag(env)
    keys = [k for g in groups.values() for k in g.keys]
    assert "RANDOM_VAR" in keys


def test_group_summary_contains_group_name(sample_env):
    groups = group_by_prefix(sample_env)
    s = group_summary(groups)
    assert "DB" in s
    assert "APP" in s


def test_group_summary_contains_key_count(sample_env):
    groups = group_by_prefix(sample_env)
    s = group_summary(groups)
    assert "2 key(s)" in s


def test_env_group_len():
    g = EnvGroup(name="TEST", keys=["A", "B", "C"])
    assert len(g) == 3
