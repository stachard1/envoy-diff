"""Live watch mode for diffing two env files continuously.

Monitors both a base and target env file for changes, recomputing
the enriched diff whenever either file is modified and invoking
a user-supplied callback with the latest DiffSummary.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envoy_diff.differ_summary import DiffSummary, build_diff_summary
from envoy_diff.parser import parse_env_file


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _file_hash(path: Path) -> str:
    """Return the MD5 hex-digest of *path* contents, or empty string if missing."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        return ""


def _load_safe(path: Path) -> dict[str, str]:
    """Parse *path* as an env file; return empty dict on any error."""
    try:
        return parse_env_file(str(path))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Public data types
# ---------------------------------------------------------------------------

@dataclass
class WatchEvent:
    """Emitted each time a change is detected during a watch loop."""

    base_path: str
    target_path: str
    summary: DiffSummary
    tick: int  # how many polling cycles have elapsed


@dataclass
class WatchState:
    """Tracks the last-seen hashes for both watched files."""

    base_hash: str = ""
    target_hash: str = ""
    ticks: int = field(default=0, init=False)

    def changed(self, base_hash: str, target_hash: str) -> bool:
        return base_hash != self.base_hash or target_hash != self.target_hash

    def update(self, base_hash: str, target_hash: str) -> None:
        self.base_hash = base_hash
        self.target_hash = target_hash
        self.ticks += 1


# ---------------------------------------------------------------------------
# Core watch function
# ---------------------------------------------------------------------------

def watch_env_pair(
    base_path: str,
    target_path: str,
    callback: Callable[[WatchEvent], None],
    *,
    interval: float = 1.0,
    max_ticks: Optional[int] = None,
    emit_on_start: bool = True,
) -> None:
    """Poll *base_path* and *target_path* and call *callback* on changes.

    Parameters
    ----------
    base_path:
        Path to the baseline env file.
    target_path:
        Path to the target env file.
    callback:
        Invoked with a :class:`WatchEvent` whenever either file changes.
    interval:
        Seconds between polls (default 1.0).
    max_ticks:
        Stop after this many polling cycles (useful for testing).  ``None``
        means run forever.
    emit_on_start:
        If ``True`` (default) fire the callback immediately on the first tick
        regardless of whether a change occurred, so callers always receive an
        initial snapshot.
    """
    base = Path(base_path)
    target = Path(target_path)
    state = WatchState()

    tick = 0
    while max_ticks is None or tick < max_ticks:
        bh = _file_hash(base)
        th = _file_hash(target)

        if state.changed(bh, th) or (emit_on_start and tick == 0):
            base_env = _load_safe(base)
            target_env = _load_safe(target)
            diff_summary = build_diff_summary(base_env, target_env)
            event = WatchEvent(
                base_path=base_path,
                target_path=target_path,
                summary=diff_summary,
                tick=tick,
            )
            callback(event)
            state.update(bh, th)

        tick += 1
        if max_ticks is None or tick < max_ticks:
            time.sleep(interval)
