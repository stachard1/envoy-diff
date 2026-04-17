"""Audit environment variable changes for sensitive key patterns."""

import re
from dataclasses import dataclass, field
from typing import List

from envoy_diff.differ import EnvDiffResult

# Patterns that suggest a key may be sensitive
SENSITIVE_PATTERNS = [
    re.compile(r"SECRET", re.IGNORECASE),
    re.compile(r"PASSWORD", re.IGNORECASE),
    re.compile(r"PASSWD", re.IGNORECASE),
    re.compile(r"TOKEN", re.IGNORECASE),
    re.compile(r"API_KEY", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY", re.IGNORECASE),
    re.compile(r"CREDENTIALS", re.IGNORECASE),
    re.compile(r"AUTH", re.IGNORECASE),
]


def is_sensitive(key: str) -> bool:
    """Return True if the key name matches any sensitive pattern."""
    return any(pattern.search(key) for pattern in SENSITIVE_PATTERNS)


@dataclass
class AuditResult:
    sensitive_added: List[str] = field(default_factory=list)
    sensitive_removed: List[str] = field(default_factory=list)
    sensitive_changed: List[str] = field(default_factory=list)

    @property
    def has_findings(self) -> bool:
        return bool(
            self.sensitive_added or self.sensitive_removed or self.sensitive_changed
        )

    def summary(self) -> str:
        lines = []
        for key in self.sensitive_added:
            lines.append(f"[AUDIT] Sensitive key added: {key}")
        for key in self.sensitive_removed:
            lines.append(f"[AUDIT] Sensitive key removed: {key}")
        for key in self.sensitive_changed:
            lines.append(f"[AUDIT] Sensitive key changed: {key}")
        return "\n".join(lines) if lines else "No sensitive key changes detected."


def audit_diff(result: EnvDiffResult) -> AuditResult:
    """Inspect an EnvDiffResult for changes to sensitive keys."""
    audit = AuditResult()
    for key in result.added:
        if is_sensitive(key):
            audit.sensitive_added.append(key)
    for key in result.removed:
        if is_sensitive(key):
            audit.sensitive_removed.append(key)
    for key in result.changed:
        if is_sensitive(key):
            audit.sensitive_changed.append(key)
    return audit
