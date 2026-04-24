"""Combines diffing with annotation and scoring into a single enriched result."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.annotator import annotate_diff, AnnotatedDiff, AnnotatedKey
from envoy_diff.scorer import score_diff, RiskScore
from envoy_diff.auditor import audit_diff, AuditResult


@dataclass
class EnrichedDiff:
    """Fully enriched diff result combining annotations, scoring, and audit findings."""

    diff: EnvDiffResult
    annotated: AnnotatedDiff
    score: RiskScore
    audit: AuditResult

    @property
    def has_changes(self) -> bool:
        return self.diff.has_changes

    @property
    def has_findings(self) -> bool:
        return self.audit.has_findings

    def summary(self) -> str:
        lines = []
        lines.append(f"Risk score : {self.score.value} ({self.score.level})")  
        lines.append(f"Changes    : added={len(self.diff.added)}, removed={len(self.diff.removed)}, changed={len(self.diff.changed)}")
        lines.append(f"Sensitive  : {len(self.annotated.sensitive_changes())} sensitive key(s) changed")
        if self.audit.has_findings:
            lines.append(f"Audit      : {self.audit.summary()}")
        else:
            lines.append("Audit      : no findings")
        return "\n".join(lines)

    def as_dict(self) -> dict:
        return {
            "risk_score": self.score.value,
            "risk_level": self.score.level,
            "added": list(self.diff.added.keys()),
            "removed": list(self.diff.removed.keys()),
            "changed": list(self.diff.changed.keys()),
            "sensitive_changes": [
                k.key for k in self.annotated.sensitive_changes()
            ],
            "audit_findings": [
                f.key for f in self.audit.findings
            ],
        }


def enrich_diff(
    before: Dict[str, str],
    after: Dict[str, str],
) -> EnrichedDiff:
    """Diff two environments and return a fully enriched result."""
    diff = diff_envs(before, after)
    annotated = annotate_diff(diff)
    score = score_diff(diff)
    audit = audit_diff(diff)
    return EnrichedDiff(diff=diff, annotated=annotated, score=score, audit=audit)
