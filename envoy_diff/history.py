"""Track and query snapshot history for env files."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from envoy_diff.snapshot import save_snapshot, load_snapshot

_HISTORY_INDEX = "history_index.json"


def _index_path(history_dir: str) -> Path:
    return Path(history_dir) / _HISTORY_INDEX


def _load_index(history_dir: str) -> List[Dict]:
    p = _index_path(history_dir)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def _save_index(history_dir: str, index: List[Dict]) -> None:
    Path(history_dir).mkdir(parents=True, exist_ok=True)
    with open(_index_path(history_dir), "w") as f:
        json.dump(index, f, indent=2)


def record_snapshot(env: Dict[str, str], label: str, history_dir: str) -> str:
    """Save a snapshot and register it in the history index. Returns snapshot path."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    filename = f"{label}_{ts}.json"
    snap_path = str(Path(history_dir) / filename)
    save_snapshot(env, snap_path)
    index = _load_index(history_dir)
    index.append({"label": label, "timestamp": ts, "path": snap_path})
    _save_index(history_dir, index)
    return snap_path


def list_history(history_dir: str) -> List[Dict]:
    """Return all history entries sorted by timestamp descending."""
    return sorted(_load_index(history_dir), key=lambda e: e["timestamp"], reverse=True)


def load_history_entry(entry: Dict) -> Optional[Dict[str, str]]:
    """Load env dict from a history entry."""
    return load_snapshot(entry["path"])


def get_latest(label: str, history_dir: str) -> Optional[Dict]:
    """Return the most recent history entry for a given label."""
    entries = [e for e in list_history(history_dir) if e["label"] == label]
    return entries[0] if entries else None


def purge_history(history_dir: str) -> int:
    """Delete all snapshots and the index. Returns number of entries removed."""
    index = _load_index(history_dir)
    for entry in index:
        try:
            os.remove(entry["path"])
        except FileNotFoundError:
            pass
    _save_index(history_dir, [])
    return len(index)
