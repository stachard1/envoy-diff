"""Watch an env file for changes and emit diffs on modification."""
from __future__ import annotations

import time
import hashlib
from pathlib import Path
from typing import Callable, Optional

from envoy_diff.parser import parse_env_file
from envoy_diff.reporter import generate_report, Report


def _file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    try:
        return parse_env_file(str(path))
    except Exception:
        return {}


def watch_env_file(
    path: str,
    callback: Callable[[Report], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Poll *path* every *interval* seconds.  When the file changes,
    call *callback* with a :class:`~envoy_diff.reporter.Report`
    comparing the previous state to the new state.

    Parameters
    ----------
    path:            Path to the .env file to watch.
    callback:        Called with the Report whenever a change is detected.
    interval:        Polling interval in seconds.
    max_iterations:  Stop after this many poll cycles (useful for testing).
    """
    p = Path(path)
    previous_env = _load(p)
    previous_hash = _file_hash(p) if p.exists() else ""

    iterations = 0
    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        iterations += 1

        if not p.exists():
            continue

        current_hash = _file_hash(p)
        if current_hash == previous_hash:
            continue

        current_env = _load(p)
        report = generate_report(previous_env, current_env)
        callback(report)

        previous_env = current_env
        previous_hash = current_hash
