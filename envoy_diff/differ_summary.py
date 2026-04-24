"""High-level diff summary combining diff, audit, score, and annotation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.auditor import audit_diff, AuditResult
from envoy_diff.scorer import score_diff, RiskScore
from envoy_diff.annotator import annotate_diff, AnnotatedDiff


@dataclass
class DiffSummary:
    """Aggregated summary of a diff between two environments."""

    label_a: str
    label_b: str
    diff: EnvDiffResult
    audit: AuditResult
    score: RiskScore
    annotated: AnnotatedDiff
    tags: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return self.diff.has_changes()

    @property
    def has_findings(self) -> bool:
        return self.audit.has_findings()

    @property
    def risk_level(self) -> str:
        return self.score.level

    def summary(self) -> str:
        parts = [
            f"Diff: {self.label_a} -> {self.label_b}",
            f"  Changes : {len(self.diff.added)} added, {len(self.diff.removed)} removed, {len(self.diff.changed)} changed",
            f"  Risk    : {self.score.level} (score={self.score.total:.1f})",
            f"  Findings: {len(self.audit.findings)} sensitive key(s) affected",
        ]
        return "\n".join(parts)

    def as_dict(self) -> dict:
        return {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "changes": {
                "added": list(self.diff.added),
                "removed": list(self.diff.removed),
                "changed": list(self.diff.changed),
            },
            "risk": {
                "level": self.score.level,
                "total": self.score.total,
            },
            "findings": [f.key for f in self.audit.findings],
            "sensitive_changes": [
                k.key for k in self.annotated.sensitive_changes()
            ],
        }


def build_diff_summary(
    env_a: dict,
    env_b: dict,
    label_a: str = "before",
    label_b: str = "after",
) -> DiffSummary:
    """Produce a DiffSummary from two environment dicts."""
    diff = diff_envs(env_a, env_b)
    audit = audit_diff(diff)
    score = score_diff(diff)
    annotated = annotate_diff(diff)
    return DiffSummary(
        label_a=label_a,
        label_b=label_b,
        diff=diff,
        audit=audit,
        score=score,
        annotated=annotated,
    )
