"""Tests for envoy_diff.differ_matrix."""
import pytest

from envoy_diff.differ_matrix import build_matrix, DiffMatrix, MatrixCell


@pytest.fixture()
def three_envs():
    return {
        "dev": {"APP": "1", "DB_HOST": "localhost", "DEBUG": "true"},
        "staging": {"APP": "1", "DB_HOST": "staging-db", "DEBUG": "false"},
        "prod": {"APP": "2", "DB_HOST": "prod-db"},
    }


@pytest.fixture()
def identical_envs():
    env = {"KEY": "val", "OTHER": "x"}
    return {"a": dict(env), "b": dict(env)}


def test_build_matrix_returns_diff_matrix(three_envs):
    result = build_matrix(three_envs)
    assert isinstance(result, DiffMatrix)


def test_all_pairs_count(three_envs):
    result = build_matrix(three_envs)
    # 3 envs → 3 pairs: (dev,staging), (dev,prod), (staging,prod)
    assert result.total_pairs == 3


def test_sequential_pairs_count(three_envs):
    result = build_matrix(three_envs, sequential=True)
    # sequential: (dev,staging), (staging,prod)
    assert result.total_pairs == 2


def test_labels_preserved(three_envs):
    result = build_matrix(three_envs)
    assert result.labels == ["dev", "staging", "prod"]


def test_matrix_cell_has_changes(three_envs):
    result = build_matrix(three_envs)
    cell = result.get("dev", "staging")
    assert cell is not None
    assert cell.has_changes


def test_matrix_cell_no_changes(identical_envs):
    result = build_matrix(identical_envs)
    cell = result.get("a", "b")
    assert cell is not None
    assert not cell.has_changes


def test_pairs_with_changes_filters_correctly(three_envs):
    result = build_matrix(three_envs)
    changed = result.pairs_with_changes
    assert len(changed) > 0
    for cell in changed:
        assert cell.has_changes


def test_get_returns_none_for_unknown_pair(three_envs):
    result = build_matrix(three_envs)
    assert result.get("prod", "dev") is None


def test_cell_summary_format(three_envs):
    result = build_matrix(three_envs)
    cell = result.get("dev", "staging")
    s = cell.summary()
    assert "dev → staging" in s
    assert "risk=" in s


def test_cell_summary_no_changes(identical_envs):
    result = build_matrix(identical_envs)
    cell = result.get("a", "b")
    assert "no changes" in cell.summary()


def test_matrix_summary_string(three_envs):
    result = build_matrix(three_envs)
    s = result.summary()
    assert "3 envs" in s
    assert "pairs" in s


def test_score_populated_on_cells(three_envs):
    result = build_matrix(three_envs)
    for cell in result.cells:
        assert cell.score is not None
        assert cell.score.level in ("none", "low", "medium", "high", "critical")


def test_sequential_only_adjacent_pairs(three_envs):
    result = build_matrix(three_envs, sequential=True)
    labels = [(c.label_a, c.label_b) for c in result.cells]
    assert ("dev", "staging") in labels
    assert ("staging", "prod") in labels
    assert ("dev", "prod") not in labels
