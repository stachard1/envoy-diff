"""Tests for envoy_diff.renamer."""
import pytest
from envoy_diff.renamer import (
    RenameRule,
    RenameResult,
    apply_renames,
    parse_rename_rules,
)


# ---------------------------------------------------------------------------
# parse_rename_rules
# ---------------------------------------------------------------------------

def test_parse_rename_rules_basic():
    rules = parse_rename_rules(["OLD_KEY=NEW_KEY"])
    assert len(rules) == 1
    assert rules[0].old_key == "OLD_KEY"
    assert rules[0].new_key == "NEW_KEY"


def test_parse_rename_rules_multiple():
    rules = parse_rename_rules(["A=B", "C=D"])
    assert [(r.old_key, r.new_key) for r in rules] == [("A", "B"), ("C", "D")]


def test_parse_rename_rules_invalid_format():
    with pytest.raises(ValueError, match="Invalid rename rule"):
        parse_rename_rules(["NODIRECTION"])


def test_parse_rename_rules_empty_key_raises():
    with pytest.raises(ValueError, match="empty key"):
        parse_rename_rules(["=NEW"])


def test_parse_rename_rules_empty_value_raises():
    with pytest.raises(ValueError, match="empty key"):
        parse_rename_rules(["OLD="])


# ---------------------------------------------------------------------------
# apply_renames – happy path
# ---------------------------------------------------------------------------

def test_apply_renames_renames_key():
    env = {"OLD": "value", "OTHER": "x"}
    result = apply_renames(env, [RenameRule("OLD", "NEW")])
    assert "NEW" in result.renamed
    assert "OLD" not in result.renamed
    assert result.renamed["NEW"] == "value"


def test_apply_renames_preserves_other_keys():
    env = {"A": "1", "B": "2"}
    result = apply_renames(env, [RenameRule("A", "Z")])
    assert result.renamed["B"] == "2"


def test_apply_renames_does_not_mutate_original():
    env = {"KEY": "val"}
    apply_renames(env, [RenameRule("KEY", "NEW_KEY")])
    assert "KEY" in env  # original unchanged


# ---------------------------------------------------------------------------
# apply_renames – skipped
# ---------------------------------------------------------------------------

def test_apply_renames_skips_missing_key():
    env = {"A": "1"}
    result = apply_renames(env, [RenameRule("MISSING", "X")])
    assert "MISSING" in result.skipped
    assert result.has_skipped


# ---------------------------------------------------------------------------
# apply_renames – conflicts
# ---------------------------------------------------------------------------

def test_apply_renames_conflict_when_target_exists():
    env = {"OLD": "old_val", "NEW": "existing"}
    result = apply_renames(env, [RenameRule("OLD", "NEW")])
    assert "NEW" in result.conflicts
    assert result.has_conflicts
    assert result.renamed["NEW"] == "existing"  # not overwritten


def test_apply_renames_overwrite_resolves_conflict():
    env = {"OLD": "new_val", "NEW": "existing"}
    result = apply_renames(env, [RenameRule("OLD", "NEW")], overwrite=True)
    assert not result.has_conflicts
    assert result.renamed["NEW"] == "new_val"


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_issues():
    env = {"K": "v"}
    result = apply_renames(env, [RenameRule("K", "K2")])
    assert "1 key(s) renamed" in result.summary()
    assert "skipped" not in result.summary()


def test_summary_includes_skipped_and_conflicts():
    env = {"A": "1", "B": "2"}
    rules = [RenameRule("MISSING", "X"), RenameRule("A", "B")]
    result = apply_renames(env, rules)
    s = result.summary()
    assert "skipped" in s
    assert "conflict" in s
