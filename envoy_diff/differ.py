"""Core diffing logic for comparing two sets of environment variables."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvDiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if not parts:
            return "No changes detected."
        return "Changes: " + ", ".join(parts) + "."


def diff_envs(
    before: Dict[str, str],
    after: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
) -> EnvDiffResult:
    """Compare two env dicts and return a structured diff result."""
    ignore = set(ignore_keys or [])
    result = EnvDiffResult()

    all_keys = set(before) | set(after)

    for key in sorted(all_keys):
        if key in ignore:
            continue
        in_before = key in before
        in_after = key in after

        if in_before and in_after:
            if before[key] == after[key]:
                result.unchanged[key] = before[key]
            else:
                result.changed[key] = (before[key], after[key])
        elif in_before:
            result.removed[key] = before[key]
        else:
            result.added[key] = after[key]

    return result
