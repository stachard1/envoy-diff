"""Redact sensitive values from env dicts before display or export."""

from typing import Dict
from envoy_diff.auditor import is_sensitive

REDACTED = "***REDACTED***"


def redact_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of env with sensitive values replaced."""
    return {k: (REDACTED if is_sensitive(k) else v) for k, v in env.items()}


def redact_diff(diff: dict) -> dict:
    """
    Given an EnvDiffResult-like dict (or the object itself), return a new
    structure with sensitive values redacted.

    Works with EnvDiffResult namedtuple/dataclass that has:
      added, removed, changed, unchanged
    """
    from envoy_diff.differ import EnvDiffResult

    if isinstance(diff, EnvDiffResult):
        added = {k: (REDACTED if is_sensitive(k) else v) for k, v in diff.added.items()}
        removed = {k: (REDACTED if is_sensitive(k) else v) for k, v in diff.removed.items()}
        changed = {
            k: (
                (REDACTED, REDACTED)
                if is_sensitive(k)
                else (old, new)
            )
            for k, (old, new) in diff.changed.items()
        }
        unchanged = {k: (REDACTED if is_sensitive(k) else v) for k, v in diff.unchanged.items()}
        return EnvDiffResult(added=added, removed=removed, changed=changed, unchanged=unchanged)
    raise TypeError(f"Unsupported diff type: {type(diff)}")
