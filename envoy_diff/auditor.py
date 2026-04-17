"""Auditor: detect sensitive environment variable changes in a diff result."""

from dataclasses import dataclass, field
from typing import List

from .differ import EnvDiffResult

_SENSITIVE_PATTERNS = [
    "secret",
    "password",
    "passwd",
    "token",
    "api_key",
    "apikey",
    "auth",
    "credential",
    "private_key",
    "access_key",
]


def is_sensitive(key: str) -> bool:
    """Return True if the key name suggests a sensitive value."""
    lower = key.lower()
    return any(pattern in lower for pattern in _SENSITIVE_PATTERNS)


@dataclass
class AuditResult:
    findings: List[str] = field(default_factory=list)

    @property
    def has_findings(self) -> bool:
        return len(self.findings) > 0

    @property
    def summary(self) -> str:
        if not self.has_findings:
            return "Audit passed: no sensitive keys affected."
        count = len(self.findings)
        return f"Audit warning: {count} sensitive key(s) changed."


def audit_diff(diff: EnvDiffResult) -> AuditResult:
    """Audit a diff result and return findings for sensitive key changes."""
    findings: List[str] = []

    for key in diff.added:
        if is_sensitive(key):
            findings.append(f"Added sensitive key: {key}")

    for key in diff.removed:
        if is_sensitive(key):
            findings.append(f"Removed sensitive key: {key}")

    for key in diff.changed:
        if is_sensitive(key):
            old_val, new_val = diff.changed[key]
            findings.append(f"Changed sensitive key: {key} (value updated)")

    return AuditResult(findings=findings)
