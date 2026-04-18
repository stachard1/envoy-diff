"""Tests for differ_cli module."""

import json
import pytest
from unittest.mock import patch
from pathlib import Path

from envoy_diff.differ_cli import build_diff_parser, run_diff


@pytest.fixture
def env_files(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=bar\nSHARED=same\nREMOVED=gone\n")
    b.write_text("FOO=changed\nSHARED=same\nADDED=new\n")
    return str(a), str(b)


def _args(file_a, file_b, fmt="text", audit=False, redact=False, exit_code=False):
    parser = build_diff_parser()
    argv = [file_a, file_b, "--format", fmt]
    if audit:
        argv.append("--audit")
    if redact:
        argv.append("--redact")
    if exit_code:
        argv.append("--exit-code")
    return parser.parse_args(argv)


def test_run_diff_text_output(env_files, capsys):
    a, b = env_files
    code = run_diff(_args(a, b))
    out = capsys.readouterr().out
    assert code == 0
    assert "FOO" in out


def test_run_diff_json_output(env_files, capsys):
    a, b = env_files
    code = run_diff(_args(a, b, fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "changed" in data
    assert code == 0


def test_exit_code_one_when_changes_and_flag(env_files):
    a, b = env_files
    code = run_diff(_args(a, b, exit_code=True))
    assert code == 1


def test_exit_code_zero_no_changes(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=bar\n")
    b.write_text("FOO=bar\n")
    code = run_diff(_args(str(a), str(b), exit_code=True))
    assert code == 0


def test_missing_file_returns_2(tmp_path, capsys):
    a = tmp_path / "a.env"
    a.write_text("FOO=bar\n")
    code = run_diff(_args(str(a), str(tmp_path / "missing.env")))
    assert code == 2


def test_redact_hides_sensitive(tmp_path, capsys):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("API_SECRET=old_secret\n")
    b.write_text("API_SECRET=new_secret\n")
    run_diff(_args(str(a), str(b), redact=True))
    out = capsys.readouterr().out
    assert "new_secret" not in out
    assert "old_secret" not in out


def test_audit_flag_shows_findings(tmp_path, capsys):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("DB_PASSWORD=old\n")
    b.write_text("DB_PASSWORD=new\n")
    run_diff(_args(str(a), str(b), audit=True))
    out = capsys.readouterr().out
    assert "audit" in out.lower() or "sensitive" in out.lower() or "password" in out.lower()
