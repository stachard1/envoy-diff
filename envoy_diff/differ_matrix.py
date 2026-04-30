"""Multi-environment diff matrix: compare N environments pairwise."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .differ import diff_envs, EnvDiffResult
from .scorer import score_diff, RiskScore


@dataclass
class MatrixCell:
    """A single cell in the diff matrix representing one pairwise comparison."""

    label_a: str
    label_b: str
    diff: EnvDiffResult
    score: RiskScore

    @property
    def has_changes(self) -> bool:
        return self.diff.added or self.diff.removed or self.diff.changed

    def summary(self) -> str:
        parts = []
        if self.diff.added:
            parts.append(f"+{len(self.diff.added)} added")
        if self.diff.removed:
            parts.append(f"-{len(self.diff.removed)} removed")
        if self.diff.changed:
            parts.append(f"~{len(self.diff.changed)} changed")
        change_str = ", ".join(parts) if parts else "no changes"
        return f"{self.label_a} → {self.label_b}: {change_str} [risk={self.score.level}]"


@dataclass
class DiffMatrix:
    """Pairwise diff matrix across multiple named environments."""

    labels: List[str]
    cells: List[MatrixCell] = field(default_factory=list)

    @property
    def total_pairs(self) -> int:
        return len(self.cells)

    @property
    def pairs_with_changes(self) -> List[MatrixCell]:
        return [c for c in self.cells if c.has_changes]

    def get(self, label_a: str, label_b: str) -> Optional[MatrixCell]:
        for cell in self.cells:
            if cell.label_a == label_a and cell.label_b == label_b:
                return cell
        return None

    def summary(self) -> str:
        changed = len(self.pairs_with_changes)
        return (
            f"Matrix ({len(self.labels)} envs, {self.total_pairs} pairs): "
            f"{changed} pair(s) with changes"
        )


def build_matrix(
    envs: Dict[str, Dict[str, str]],
    *,
    sequential: bool = False,
) -> DiffMatrix:
    """Build a diff matrix from a mapping of label -> env dict.

    Args:
        envs: Ordered mapping of environment label to key/value dict.
        sequential: If True, only compare adjacent pairs (a→b, b→c, …).
                    If False (default), compare all ordered pairs (i < j).
    """
    labels = list(envs.keys())
    matrix = DiffMatrix(labels=labels)

    if sequential:
        pairs: List[Tuple[str, str]] = [
            (labels[i], labels[i + 1]) for i in range(len(labels) - 1)
        ]
    else:
        pairs = [
            (labels[i], labels[j])
            for i in range(len(labels))
            for j in range(i + 1, len(labels))
        ]

    for label_a, label_b in pairs:
        diff = diff_envs(envs[label_a], envs[label_b])
        score = score_diff(diff)
        matrix.cells.append(
            MatrixCell(label_a=label_a, label_b=label_b, diff=diff, score=score)
        )

    return matrix
