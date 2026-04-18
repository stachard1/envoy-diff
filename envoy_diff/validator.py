"""Validate environment variables against simple rule sets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str = "warning"  # "error" or "warning"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        if not self.has_issues:
            return "All variables passed validation."
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) found."
        )


def _is_blank(value: str) -> bool:
    return value.strip() == ""


def _has_invalid_chars(key: str) -> bool:
    return not all(c.isalnum() or c == "_" for c in key)


def validate_env(
    env: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    disallow_blank: bool = True,
) -> ValidationResult:
    """Validate an env dict against optional rules."""
    result = ValidationResult()

    for key, value in env.items():
        if _has_invalid_chars(key):
            result.issues.append(
                ValidationIssue(key, f"Key '{key}' contains invalid characters.", "error")
            )
        if disallow_blank and _is_blank(value):
            result.issues.append(
                ValidationIssue(key, f"Key '{key}' has a blank value.", "warning")
            )

    for req in required_keys or []:
        if req not in env:
            result.issues.append(
                ValidationIssue(req, f"Required key '{req}' is missing.", "error")
            )

    return result
