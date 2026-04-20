"""Tests for envoy_diff.patch_cli."""

import json
import os
import pytest

from envoy_diff.patch_cli import cmd_patch, build_patch_parser


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    base.write_text("HOST=localhost\nPORT=5432\nDEBUG=false\n")
    target.write_text("HOST=prod.db\nPORT=5432\nNEW_KEY=hello\n")
    return str(base), str(target)


def _args(base, target, fmt="text", skip=None, out=None):
    parser = build_patch_parser()
    argv = [base, target, "--format", fmt]
    if skip:
        argv += ["--skip"] + skip
    if out:
        argv += ["--out", out]
    return parser.parse_args(argv)


def test_cmd_patch_returns_zero(env_files):
    base, target = env_files
    args = _args(base, target)
    assert cmd_patch(args) == 0


def test_cmd_patch_text_output_contains_keys(env_files, capsys):
    base, target = env_files
    args = _args(base, target)
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "HOST=prod.db" in out
    assert "NEW_KEY=hello" in out
    assert "DEBUG" not in out


def test_cmd_patch_json_output(env_files, capsys):
    base, target = env_files
    args = _args(base, target, fmt="json")
    cmd_patch(args)
    data = json.loads(capsys.readouterr().out)
    assert data["patched"]["HOST"] == "prod.db"
    assert "NEW_KEY" in data["patched"]
    assert "DEBUG" not in data["patched"]


def test_cmd_patch_skip_key(env_files, capsys):
    base, target = env_files
    args = _args(base, target, skip=["HOST"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "HOST=localhost" in out


def test_cmd_patch_writes_file(env_files, tmp_path):
    base, target = env_files
    out_file = str(tmp_path / "patched.env")
    args = _args(base, target, out=out_file)
    cmd_patch(args)
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "HOST=prod.db" in content


def test_cmd_patch_missing_base_returns_2(env_files, tmp_path):
    _, target = env_files
    args = _args("/nonexistent.env", target)
    assert cmd_patch(args) == 2


def test_cmd_patch_json_includes_applied_skipped(env_files, capsys):
    base, target = env_files
    args = _args(base, target, fmt="json", skip=["HOST"])
    cmd_patch(args)
    data = json.loads(capsys.readouterr().out)
    assert "applied" in data
    assert "skipped" in data
    assert "HOST" in data["skipped"]
