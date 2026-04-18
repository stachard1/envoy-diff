"""Merge multiple env dicts with conflict detection."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MergeConflict:
    key: str
    values: List[str]

    def __str__(self) -> str:
        vals = ", ".join(f"{v!r}" for v in self.values)
        return f"{self.key}: [{vals}]"


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: List[MergeConflict] = field(default_factory=list)

    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        if not self.has_conflicts():
            return f"Merged {len(self.merged)} keys, no conflicts."
        return (
            f"Merged {len(self.merged)} keys, "
            f"{len(self.conflicts)} conflict(s): "
            + "; ".join(str(c) for c in self.conflicts)
        )


def merge_envs(
    *envs: Dict[str, str],
    strategy: str = "last",
    labels: Optional[List[str]] = None,
) -> MergeResult:
    """Merge env dicts.

    strategy:
      'last'  – last writer wins (default)
      'first' – first writer wins
      'error' – raise on conflict
    """
    if labels and len(labels) != len(envs):
        raise ValueError("labels length must match number of envs")

    merged: Dict[str, str] = {}
    origin: Dict[str, int] = {}
    conflicts: List[MergeConflict] = []
    conflict_keys: set = set()

    for idx, env in enumerate(envs):
        for key, value in env.items():
            if key in merged and merged[key] != value:
                if key not in conflict_keys:
                    conflict_keys.add(key)
                    conflicts.append(MergeConflict(key=key, values=[merged[key], value]))
                else:
                    for c in conflicts:
                        if c.key == key and value not in c.values:
                            c.values.append(value)
                if strategy == "error":
                    raise ValueError(f"Conflict on key '{key}'")
                if strategy == "first":
                    continue
                merged[key] = value
                origin[key] = idx
            else:
                merged[key] = value
                origin[key] = idx

    return MergeResult(merged=merged, conflicts=conflicts)
