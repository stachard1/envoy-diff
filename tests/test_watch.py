"""Tests for envoy_diff.watch."""
import time
import threading
from pathlib import Path

import pytest

from envoy_diff.watch import watch_env_file
from envoy_diff.reporter import Report


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def test_callback_triggered_on_change(tmp_path):
    env_file = tmp_path / ".env"
    _write(env_file, "FOO=bar\n")

    reports: list[Report] = []

    def run():
        watch_env_file(
            str(env_file),
            callback=reports.append,
            interval=0.05,
            max_iterations=6,
        )

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(0.1)
    _write(env_file, "FOO=bar\nBAZ=qux\n")
    t.join(timeout=2)

    assert len(reports) >= 1
    assert isinstance(reports[0], Report)


def test_callback_receives_correct_diff(tmp_path):
    env_file = tmp_path / ".env"
    _write(env_file, "A=1\nB=2\n")

    reports: list[Report] = []

    def run():
        watch_env_file(
            str(env_file),
            callback=reports.append,
            interval=0.05,
            max_iterations=6,
        )

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(0.1)
    _write(env_file, "A=1\nC=3\n")
    t.join(timeout=2)

    assert reports
    diff = reports[0].diff
    assert "C" in diff.added
    assert "B" in diff.removed


def test_no_callback_when_file_unchanged(tmp_path):
    env_file = tmp_path / ".env"
    _write(env_file, "X=1\n")

    reports: list[Report] = []

    watch_env_file(
        str(env_file),
        callback=reports.append,
        interval=0.05,
        max_iterations=4,
    )

    assert reports == []
