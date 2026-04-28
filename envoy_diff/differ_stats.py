"""Statistics aggregation over a diff result."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_diff.differ import EnvDiffResult, diff_envs
from envoy_diff.auditor import audit_diff
from envoy_diff.scorer import score_diff
from envoy_diff.tagger import tag_key


@dataclass
class DiffStats:
    added: int = 0
    removed: int = 0
    changed: int = 0
    unchanged: int = 0
    sensitive_changes: int = 0
    risk_score: float = 0.0
    risk_level: str = "none"
    tag_counts: Dict[str, int] = field(default_factory=dict)
    top_changed_keys: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.changed

    @property
    def has_changes(self) -> bool:
        return self.total_changes > 0

    def summary(self) -> str:
        parts = [
            f"added={self.added}",
            f"removed={self.removed}",
            f"changed={self.changed}",
            f"unchanged={self.unchanged}",
            f"sensitive={self.sensitive_changes}",
            f"risk={self.risk_level}({self.risk_score:.1f})",
        ]
        return "DiffStats(" + ", ".join(parts) + ")"


def compute_stats(
    before: Dict[str, str],
    after: Dict[str, str],
    top_n: int = 5,
) -> DiffStats:
    """Compute aggregated statistics for the diff between *before* and *after*."""
    result: EnvDiffResult = diff_envs(before, after)
    audit = audit_diff(result)
    score = score_diff(result)

    tag_counts: Dict[str, int] = {}
    for key in list(result.added) + list(result.removed) + list(result.changed):
        for tag in tag_key(key):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    sensitive_changes = len(
        [f for f in audit.findings if f.key in result.added or f.key in result.removed or f.key in result.changed]
    )

    all_changed = sorted(result.added | result.removed | result.changed)
    top_changed = all_changed[:top_n]

    return DiffStats(
        added=len(result.added),
        removed=len(result.removed),
        changed=len(result.changed),
        unchanged=len(result.unchanged),
        sensitive_changes=sensitive_changes,
        risk_score=score.score,
        risk_level=score.level,
        tag_counts=tag_counts,
        top_changed_keys=top_changed,
    )


def stats_as_dict(stats: DiffStats) -> dict:
    return {
        "added": stats.added,
        "removed": stats.removed,
        "changed": stats.changed,
        "unchanged": stats.unchanged,
        "total_changes": stats.total_changes,
        "sensitive_changes": stats.sensitive_changes,
        "risk_score": stats.risk_score,
        "risk_level": stats.risk_level,
        "tag_counts": stats.tag_counts,
        "top_changed_keys": stats.top_changed_keys,
    }
