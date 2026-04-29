"""Generate a structured changelog from a sequence of env diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from envoy_diff.differ import diff_envs, EnvDiffResult
from envoy_diff.auditor import audit_diff
from envoy_diff.scorer import score_diff


@dataclass
class ChangelogEntry:
    label: str
    timestamp: str
    diff: EnvDiffResult
    risk_level: str
    sensitive_keys: List[str] = field(default_factory=list)

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
        sensitive_str = f", {len(self.sensitive_keys)} sensitive" if self.sensitive_keys else ""
        return f"[{self.label}] {change_str}{sensitive_str} (risk: {self.risk_level})"


@dataclass
class Changelog:
    entries: List[ChangelogEntry] = field(default_factory=list)

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    def entries_with_changes(self) -> List[ChangelogEntry]:
        return [e for e in self.entries if e.has_changes]

    def high_risk_entries(self) -> List[ChangelogEntry]:
        return [e for e in self.entries if e.risk_level in ("high", "critical")]

    def summary(self) -> str:
        changed = len(self.entries_with_changes())
        high = len(self.high_risk_entries())
        return (
            f"{self.total_entries} entries, {changed} with changes, "
            f"{high} high-risk"
        )


def build_changelog(
    snapshots: List[tuple[str, dict, dict]],
    timestamp: Optional[str] = None,
) -> Changelog:
    """Build a Changelog from a list of (label, before_env, after_env) tuples."""
    entries: List[ChangelogEntry] = []
    ts = timestamp or datetime.utcnow().isoformat()

    for label, before, after in snapshots:
        diff = diff_envs(before, after)
        audit = audit_diff(diff)
        score = score_diff(diff)
        sensitive = [f.key for f in audit.findings]
        entry = ChangelogEntry(
            label=label,
            timestamp=ts,
            diff=diff,
            risk_level=score.level,
            sensitive_keys=sensitive,
        )
        entries.append(entry)

    return Changelog(entries=entries)
