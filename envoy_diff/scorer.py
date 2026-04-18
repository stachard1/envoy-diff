"""Risk scorer for environment variable diffs."""
from dataclasses import dataclass, field
from typing import Dict
from envoy_diff.differ import EnvDiffResult
from envoy_diff.auditor import audit_diff

SEVERITY_WEIGHTS = {
    "added_sensitive": 3,
    "removed_sensitive": 2,
    "changed_sensitive": 4,
    "added": 1,
    "removed": 2,
    "changed": 1,
}


@dataclass
class RiskScore:
    total: int
    breakdown: Dict[str, int] = field(default_factory=dict)
    level: str = "low"


def _level(score: int) -> str:
    if score == 0:
        return "none"
    if score < 5:
        return "low"
    if score < 15:
        return "medium"
    return "high"


def score_diff(diff: EnvDiffResult) -> RiskScore:
    audit = audit_diff(diff)
    sensitive_keys = {f.key for f in audit.findings}

    breakdown: Dict[str, int] = {}

    for key in diff.added:
        k = "added_sensitive" if key in sensitive_keys else "added"
        breakdown[k] = breakdown.get(k, 0) + SEVERITY_WEIGHTS[k]

    for key in diff.removed:
        k = "removed_sensitive" if key in sensitive_keys else "removed"
        breakdown[k] = breakdown.get(k, 0) + SEVERITY_WEIGHTS[k]

    for key in diff.changed:
        k = "changed_sensitive" if key in sensitive_keys else "changed"
        breakdown[k] = breakdown.get(k, 0) + SEVERITY_WEIGHTS[k]

    total = sum(breakdown.values())
    return RiskScore(total=total, breakdown=breakdown, level=_level(total))
