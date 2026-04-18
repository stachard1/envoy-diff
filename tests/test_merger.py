import pytest
from envoy_diff.merger import merge_envs, MergeResult, MergeConflict


def test_merge_no_conflicts():
    a = {"FOO": "1", "BAR": "2"}
    b = {"BAZ": "3"}
    result = merge_envs(a, b)
    assert result.merged == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert not result.has_conflicts()


def test_merge_last_wins_by_default():
    a = {"FOO": "old"}
    b = {"FOO": "new"}
    result = merge_envs(a, b)
    assert result.merged["FOO"] == "new"
    assert result.has_conflicts()


def test_merge_first_wins():
    a = {"FOO": "first"}
    b = {"FOO": "second"}
    result = merge_envs(a, b, strategy="first")
    assert result.merged["FOO"] == "first"
    assert result.has_conflicts()


def test_merge_error_strategy_raises():
    a = {"FOO": "1"}
    b = {"FOO": "2"}
    with pytest.raises(ValueError, match="Conflict on key 'FOO'"):
        merge_envs(a, b, strategy="error")


def test_merge_conflict_lists_values():
    a = {"KEY": "alpha"}
    b = {"KEY": "beta"}
    result = merge_envs(a, b)
    assert len(result.conflicts) == 1
    c = result.conflicts[0]
    assert c.key == "KEY"
    assert "alpha" in c.values
    assert "beta" in c.values


def test_merge_three_envs_accumulates_conflict_values():
    a = {"X": "1"}
    b = {"X": "2"}
    c = {"X": "3"}
    result = merge_envs(a, b, c)
    assert result.merged["X"] == "3"
    assert len(result.conflicts[0].values) == 3


def test_merge_summary_no_conflicts():
    result = merge_envs({"A": "1"}, {"B": "2"})
    assert "no conflicts" in result.summary()


def test_merge_summary_with_conflicts():
    result = merge_envs({"A": "1"}, {"A": "2"})
    assert "conflict" in result.summary()
    assert "A" in result.summary()


def test_labels_wrong_length_raises():
    with pytest.raises(ValueError, match="labels length"):
        merge_envs({"A": "1"}, {"B": "2"}, labels=["only-one"])


def test_labels_correct_length_ok():
    result = merge_envs({"A": "1"}, {"B": "2"}, labels=["env1", "env2"])
    assert result.merged == {"A": "1", "B": "2"}


def test_same_value_no_conflict():
    a = {"PORT": "8080"}
    b = {"PORT": "8080"}
    result = merge_envs(a, b)
    assert not result.has_conflicts()
    assert result.merged["PORT"] == "8080"
