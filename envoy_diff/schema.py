"""Schema validation: check env vars conform to expected types/patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SchemaRule:
    key: str
    pattern: Optional[str] = None
    required: bool = False
    allowed_values: Optional[List[str]] = None


@dataclass
class SchemaViolation:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class SchemaResult:
    violations: List[SchemaViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)

    @property
    def errors(self) -> List[SchemaViolation]:
        return [v for v in self.violations if v.severity == "error"]

    @property
    def warnings(self) -> List[SchemaViolation]:
        return [v for v in self.violations if v.severity == "warning"]

    def summary(self) -> str:
        if not self.has_violations:
            return "Schema OK: no violations found."
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) "
            f"from schema validation."
        )


def validate_schema(
    env: Dict[str, str],
    rules: List[SchemaRule],
) -> SchemaResult:
    result = SchemaResult()

    for rule in rules:
        value = env.get(rule.key)

        if value is None:
            if rule.required:
                result.violations.append(
                    SchemaViolation(
                        key=rule.key,
                        message=f"Required key '{rule.key}' is missing.",
                        severity="error",
                    )
                )
            continue

        if rule.allowed_values is not None and value not in rule.allowed_values:
            result.violations.append(
                SchemaViolation(
                    key=rule.key,
                    message=(
                        f"Value '{value}' for '{rule.key}' not in allowed values: "
                        f"{rule.allowed_values}."
                    ),
                    severity="error",
                )
            )

        if rule.pattern is not None and not re.fullmatch(rule.pattern, value):
            result.violations.append(
                SchemaViolation(
                    key=rule.key,
                    message=(
                        f"Value '{value}' for '{rule.key}' does not match "
                        f"pattern '{rule.pattern}'."
                    ),
                    severity="warning",
                )
            )

    return result
