"""Mask sensitive values in env dicts for safe display or logging."""

from typing import Dict, Optional
from envoy_diff.auditor import is_sensitive

MASK_VALUE = "****"


def mask_env(env: Dict[str, str], placeholder: str = MASK_VALUE) -> Dict[str, str]:
    """Return a copy of env with sensitive values replaced by placeholder."""
    return {
        key: (placeholder if is_sensitive(key) else value)
        for key, value in env.items()
    }


def mask_value(key: str, value: str, placeholder: str = MASK_VALUE) -> str:
    """Return masked value if key is sensitive, otherwise return value."""
    return placeholder if is_sensitive(key) else value


def mask_dict(data: Dict[str, str], keys: Optional[list] = None, placeholder: str = MASK_VALUE) -> Dict[str, str]:
    """Mask a specific list of keys, or all sensitive keys if none provided."""
    if keys is not None:
        return {
            k: (placeholder if k in keys else v)
            for k, v in data.items()
        }
    return mask_env(data, placeholder)


def unmask_count(original: Dict[str, str], masked: Dict[str, str]) -> int:
    """Return the number of keys that were masked (value differs from original)."""
    return sum(1 for k in original if masked.get(k) != original[k])
