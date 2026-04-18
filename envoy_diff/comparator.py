"""Compare two named profiles or snapshots with risk scoring and audit."""
from dataclasses import dataclass
from typing import Optional

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.auditor import audit_diff, AuditResult
from envoy_diff.scorer import score_diff, RiskScore
from envoy_diff.profile import load_profile
from envoy_diff.snapshot import load_snapshot


@dataclass
class CompareResult:
    label_a: str
    label_b: str
    diff: EnvDiffResult
    audit: AuditResult
    score: RiskScore

    def summary(self) -> str:
        lines = [
            f"Comparing '{self.label_a}' → '{self.label_b}'",
            self.diff.summary(),
            self.audit.summary(),
            f"Risk: {self.score.level} ({self.score.total})",
        ]
        return "\n".join(lines)


def compare_profiles(name_a: str, name_b: str, profile_dir: str = ".envoy_profiles") -> CompareResult:
    env_a = load_profile(name_a, profile_dir) or {}
    env_b = load_profile(name_b, profile_dir) or {}
    return _build_result(name_a, name_b, env_a, env_b)


def compare_snapshots(path_a: str, path_b: str) -> CompareResult:
    env_a = load_snapshot(path_a) or {}
    env_b = load_snapshot(path_b) or {}
    return _build_result(path_a, path_b, env_a, env_b)


def _build_result(label_a: str, label_b: str, env_a: dict, env_b: dict) -> CompareResult:
    diff = diff_envs(env_a, env_b)
    audit = audit_diff(diff)
    score = score_diff(diff)
    return CompareResult(label_a=label_a, label_b=label_b, diff=diff, audit=audit, score=score)
