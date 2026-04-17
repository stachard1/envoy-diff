"""Snapshot persistence: save and load environment snapshots to disk."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_snapshot(env: dict[str, str], path: str) -> None:
    """Persist *env* as a JSON snapshot at *path*."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    payload: dict[str, Any] = {
        "created_at": _now_iso(),
        "env": env,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def load_snapshot(path: str) -> dict[str, Any]:
    """Load and return the snapshot dict from *path*.

    Raises FileNotFoundError when the file does not exist.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def snapshot_metadata(path: str) -> dict[str, str]:
    """Return metadata fields (everything except 'env') from a snapshot."""
    data = load_snapshot(path)
    return {k: v for k, v in data.items() if k != "env"}
