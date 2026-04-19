import pytest
from envoy_diff.transformer import TransformRule, apply_transforms


@pytest.fixture
def env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "staging", "DEBUG": "true"}


def test_delete_key(env):
    rules = [TransformRule(key_pattern="DEBUG", action="delete")]
    result = apply_transforms(env, rules)
    assert "DEBUG" not in result.env
    assert "delete:DEBUG" in result.applied


def test_rename_key(env):
    rules = [TransformRule(key_pattern="DB_HOST", action="rename", target="DATABASE_HOST")]
    result = apply_transforms(env, rules)
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert "rename:DB_HOST->DATABASE_HOST" in result.applied


def test_set_value(env):
    rules = [TransformRule(key_pattern="APP_ENV", action="set", target="production")]
    result = apply_transforms(env, rules)
    assert result.env["APP_ENV"] == "production"


def test_remap_value(env):
    rules = [TransformRule(key_pattern="APP_ENV", action="remap", value_map={"staging": "prod"})]
    result = apply_transforms(env, rules)
    assert result.env["APP_ENV"] == "prod"


def test_remap_no_match_keeps_original(env):
    rules = [TransformRule(key_pattern="APP_ENV", action="remap", value_map={"other": "prod"})]
    result = apply_transforms(env, rules)
    assert result.env["APP_ENV"] == "staging"


def test_transform_fn(env):
    rules = [TransformRule(key_pattern="DB_PORT", action="transform", transform_fn=lambda v: str(int(v) + 1))]
    result = apply_transforms(env, rules)
    assert result.env["DB_PORT"] == "5433"


def test_pattern_matches_multiple_keys(env):
    rules = [TransformRule(key_pattern="DB_.*", action="delete")]
    result = apply_transforms(env, rules)
    assert "DB_HOST" not in result.env
    assert "DB_PORT" not in result.env
    assert "APP_ENV" in result.env


def test_unmatched_rule_goes_to_skipped(env):
    rules = [TransformRule(key_pattern="NONEXISTENT", action="delete")]
    result = apply_transforms(env, rules)
    assert "NONEXISTENT" in result.skipped


def test_multiple_rules_applied_in_order(env):
    rules = [
        TransformRule(key_pattern="APP_ENV", action="set", target="production"),
        TransformRule(key_pattern="APP_ENV", action="rename", target="ENVIRONMENT"),
    ]
    result = apply_transforms(env, rules)
    assert result.env.get("ENVIRONMENT") == "production"
    assert "APP_ENV" not in result.env
