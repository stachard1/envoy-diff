"""High-level summary generator combining diff, audit, score, and tags."""
from dataclasses import dataclass
from typing import Dict, Any

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.auditor import audit_diff, AuditResult
from envoy_diff.scorer import score_diff, RiskScore
from envoy_diff.tagger import tag_env, TaggedEnv


@dataclass
class EnvSummary:
    diff: EnvDiffResult
    audit: AuditResult
    score: RiskScore
    tags_before: TaggedEnv
    tags_after: TaggedEnv


def summarize(before: Dict[str, str], after: Dict[str, str]) -> EnvSummary:
    """Produce a combined summary of all analysis for two env snapshots."""
    diff = diff_envs(before, after)
    audit = audit_diff(diff)
    score = score_diff(diff)
    tags_before = tag_env(before)
    tags_after = tag_env(after)
    return EnvSummary(
        diff=diff,
        audit=audit,
        score=score,
        tags_before=tags_before,
        tags_after=tags_after,
    )


def summary_as_dict(s: EnvSummary) -> Dict[str, Any]:
    """Serialize an EnvSummary to a plain dict suitable for JSON export."""
    return {
        "diff": {
            "added": s.diff.added,
            "removed": s.diff.removed,
            "changed": {k: {"before": b, "after": a} for k, (b, a) in s.diff.changed.items()},
            "unchanged_count": len(s.diff.unchanged),
        },
        "audit": {
            "findings": [
                {"key": f.key, "reason": f.reason, "severity": f.severity}
                for f in s.audit.findings
            ]
        },
        "score": {
            "total": s.score.total,
            "level": s.score.level,
        },
        "tags": {
            "before": {k: list(v) for k, v in s.tags_before.tags.items()},
            "after": {k: list(v) for k, v in s.tags_after.tags.items()},
        },
    }
