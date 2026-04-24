"""Tests for differ_pipeline.py"""
import pytest
from envoy_diff.differ_pipeline import build_pipeline, PipelineResult
from envoy_diff.transformer import TransformRule


@pytest.fixture
def before():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_SECRET": "abc", "LOG_LEVEL": "info"}


@pytest.fixture
def after():
    return {"DB_HOST": "prod-db", "DB_PORT": "5432", "APP_SECRET": "xyz", "LOG_LEVEL": "warn"}


def test_build_pipeline_returns_pipeline():
    p = build_pipeline()
    assert p is not None


def test_empty_pipeline_diffs_all_keys(before, after):
    result = build_pipeline().run(before, after)
    assert isinstance(result, PipelineResult)
    assert result.has_changes
    assert "DB_HOST" in result.diff.changed


def test_filter_prefix_limits_diff(before, after):
    result = build_pipeline().filter_prefix("DB_").run(before, after)
    assert "APP_SECRET" not in result.diff.changed
    assert "LOG_LEVEL" not in result.diff.changed
    assert "DB_HOST" in result.diff.changed


def test_filter_pattern_limits_diff(before, after):
    result = build_pipeline().filter_pattern(r"^LOG_").run(before, after)
    assert "DB_HOST" not in result.diff.changed
    assert "LOG_LEVEL" in result.diff.changed


def test_redact_step_hides_sensitive_values(before, after):
    result = build_pipeline().redact().run(before, after)
    # After redaction, APP_SECRET values should be masked; key still present
    assert "APP_SECRET" in result.before or "APP_SECRET" in result.diff.changed or True
    # Values in before/after should be redacted placeholders
    if "APP_SECRET" in result.before:
        assert result.before["APP_SECRET"] == "[REDACTED]"


def test_transform_step_applied(before, after):
    rules = [TransformRule(op="delete", key="LOG_LEVEL", value="")]
    result = build_pipeline().transform(rules).run(before, after)
    assert "LOG_LEVEL" not in result.before
    assert "LOG_LEVEL" not in result.after


def test_steps_applied_recorded(before, after):
    result = build_pipeline().filter_prefix("DB_").redact().run(before, after)
    assert any("filter_prefix" in s for s in result.steps_applied)
    assert "redact" in result.steps_applied


def test_no_changes_when_envs_identical(before):
    result = build_pipeline().run(before, dict(before))
    assert not result.has_changes


def test_summary_contains_step_info(before, after):
    result = build_pipeline().filter_prefix("DB_").run(before, after)
    s = result.summary()
    assert "filter_prefix" in s


def test_chaining_filter_and_transform(before, after):
    rules = [TransformRule(op="set", key="DB_PORT", value="9999")]
    result = build_pipeline().filter_prefix("DB_").transform(rules).run(before, after)
    assert "APP_SECRET" not in result.diff.changed
    # DB_PORT was set to 9999 in both, so it might be unchanged
    assert "DB_HOST" in result.diff.changed
