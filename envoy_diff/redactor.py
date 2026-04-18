"""Redact sensitive values from env dicts and diff results."""

from envoy_diff.auditor import is_sensitive

REDACTED = "***REDACTED***"


def redact_env(env: dict) -> dict:
    """Return a copy of env with sensitive values replaced."""
    return {k: (REDACTED if is_sensitive(k) else v) for k, v in env.items()}


def redact_diff(result) -> object:
    """Return a new EnvDiffResult with sensitive values redacted."""
    from envoy_diff.differ import EnvDiffResult

    added = {k: (REDACTED if is_sensitive(k) else v) for k, v in result.added.items()}
    removed = {k: (REDACTED if is_sensitive(k) else v) for k, v in result.removed.items()}
    changed = {
        k: (REDACTED, REDACTED) if is_sensitive(k) else (old, new)
        for k, (old, new) in result.changed.items()
    }
    unchanged = result.unchanged

    return EnvDiffResult(added=added, removed=removed, changed=changed, unchanged=unchanged)
