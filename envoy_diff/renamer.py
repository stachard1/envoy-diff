"""Bulk key renaming for environment variable maps."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameRule:
    """A single rename instruction: old_key -> new_key."""
    old_key: str
    new_key: str


@dataclass
class RenameResult:
    renamed: Dict[str, str] = field(default_factory=dict)   # new_key -> value
    skipped: List[str] = field(default_factory=list)         # old_keys not found
    conflicts: List[str] = field(default_factory=list)       # new_keys already present

    @property
    def has_skipped(self) -> bool:
        return bool(self.skipped)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        parts = [f"{len(self.renamed)} key(s) renamed"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (not found)")
        if self.conflicts:
            parts.append(f"{len(self.conflicts)} conflict(s) (target key exists)")
        return ", ".join(parts)


def parse_rename_rules(raw: List[str]) -> List[RenameRule]:
    """Parse 'OLD=NEW' strings into RenameRule objects."""
    rules: List[RenameRule] = []
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid rename rule (expected OLD=NEW): {item!r}")
        old, new = item.split("=", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError(f"Rename rule has empty key: {item!r}")
        rules.append(RenameRule(old_key=old, new_key=new))
    return rules


def apply_renames(
    env: Dict[str, str],
    rules: List[RenameRule],
    overwrite: bool = False,
) -> RenameResult:
    """Apply rename rules to *env* and return a RenameResult.

    The original dict is not mutated; the result's ``renamed`` dict
    contains the full env with keys substituted.

    Args:
        env: Source environment mapping.
        rules: Ordered list of rename rules to apply.
        overwrite: When True, allow renaming even if *new_key* already
                   exists in the env (the old value is replaced).
    """
    result = RenameResult(renamed=dict(env))

    for rule in rules:
        if rule.old_key not in result.renamed:
            result.skipped.append(rule.old_key)
            continue
        if rule.new_key in result.renamed and not overwrite:
            result.conflicts.append(rule.new_key)
            continue
        value = result.renamed.pop(rule.old_key)
        result.renamed[rule.new_key] = value

    return result
