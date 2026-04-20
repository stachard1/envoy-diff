"""Apply a diff result as a patch to produce a new env dict."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import EnvDiffResult, diff_envs


@dataclass
class PatchResult:
    patched: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def has_skipped(self) -> bool:
        return bool(self.skipped)

    def summary(self) -> str:
        parts = [f"applied={len(self.applied)}", f"skipped={len(self.skipped)}"]
        return ", ".join(parts)


def apply_patch(
    base: Dict[str, str],
    diff: EnvDiffResult,
    skip_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Produce a new env by applying *diff* on top of *base*.

    Keys listed in *skip_keys* are left untouched in the base.
    """
    skip = set(skip_keys or [])
    patched = dict(base)
    applied: List[str] = []
    skipped: List[str] = []

    for key in diff.added:
        if key in skip:
            skipped.append(key)
            continue
        patched[key] = diff.added[key]
        applied.append(key)

    for key in diff.removed:
        if key in skip:
            skipped.append(key)
            continue
        patched.pop(key, None)
        applied.append(key)

    for key, (_, new_val) in diff.changed.items():
        if key in skip:
            skipped.append(key)
            continue
        patched[key] = new_val
        applied.append(key)

    return PatchResult(patched=patched, applied=applied, skipped=skipped)


def patch_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    skip_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Convenience: diff *base* → *target* then apply the patch."""
    diff = diff_envs(base, target)
    return apply_patch(base, diff, skip_keys=skip_keys)
