"""Persist and load env snapshots for later comparison."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Union


SNAPSHOT_VERSION = 1


def save_snapshot(
    env: dict[str, str],
    path: Union[str, Path],
    label: Optional[str] = None,
) -> None:
    """Serialise *env* to a JSON snapshot file."""
    data = {
        "version": SNAPSHOT_VERSION,
        "timestamp": time.time(),
        "label": label or "",
        "env": env,
    }
    Path(path).write_text(json.dumps(data, indent=2))


def load_snapshot(path: Union[str, Path]) -> dict[str, str]:
    """Load an env dict from a previously saved snapshot file."""
    raw = json.loads(Path(path).read_text())
    if raw.get("version") != SNAPSHOT_VERSION:
        raise ValueError(
            f"Unsupported snapshot version: {raw.get('version')!r}"
        )
    return raw["env"]


def snapshot_metadata(path: Union[str, Path]) -> dict:
    """Return metadata (timestamp, label, version) without loading the full env."""
    raw = json.loads(Path(path).read_text())
    return {
        "version": raw.get("version"),
        "timestamp": raw.get("timestamp"),
        "label": raw.get("label", ""),
        "key_count": len(raw.get("env", {})),
    }
