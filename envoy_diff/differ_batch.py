"""Batch diff: compare multiple pairs of env files and aggregate results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.scorer import score_diff, RiskScore
from envoy_diff.auditor import audit_diff, AuditResult


@dataclass
class BatchEntry:
    label: str
    diff: EnvDiffResult
    score: RiskScore
    audit: AuditResult

    @property
    def has_changes(self) -> bool:
        return self.diff.has_changes()

    @property
    def has_findings(self) -> bool:
        return self.audit.has_findings()


@dataclass
class BatchDiffResult:
    entries: List[BatchEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.has_changes)

    @property
    def flagged_count(self) -> int:
        return sum(1 for e in self.entries if e.has_findings)

    @property
    def max_score(self) -> float:
        if not self.entries:
            return 0.0
        return max(e.score.total for e in self.entries)

    def summary(self) -> str:
        return (
            f"{self.total} pair(s) compared: "
            f"{self.changed_count} with changes, "
            f"{self.flagged_count} with sensitive findings, "
            f"max risk score {self.max_score:.1f}"
        )


def batch_diff(
    pairs: List[Tuple[str, Dict[str, str], Dict[str, str]]]
) -> BatchDiffResult:
    """Diff a list of (label, before_env, after_env) tuples.

    Args:
        pairs: sequence of (label, before, after) triples.

    Returns:
        BatchDiffResult aggregating all per-pair results.
    """
    result = BatchDiffResult()
    for label, before, after in pairs:
        diff = diff_envs(before, after)
        score = score_diff(diff)
        audit = audit_diff(diff)
        result.entries.append(BatchEntry(label=label, diff=diff, score=score, audit=audit))
    return result
