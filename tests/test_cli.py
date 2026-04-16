"""Tests for envoy_diff.cli."""
import json
import os
import textwrap
import pytest
from envoy_diff.cli import main


@pytest.fixture()
def env_files(tmp_path):
    before = tmp_path / "before.env"
    after = tmp_path / "after.env"
    before.write_text(textwrap.dedent("""\
        FOO=bar
        REMOVED=gone
        CHANGED=old
    """))
    after.write_text(textwrap.dedent("""\
        FOO=bar
        ADDED=new
        CHANGED=new
    """))
    return str(before), str(after)


def test_exit_code_zero_no_changes(tmp_path):
    f = tmp_path / "same.env"
    f.write_text("FOO=bar\n")
    assert main([str(f), str(f), "--no-color"]) == 0


def test_exit_code_zero_with_changes_no_flag(env_files):
    before, after = env_files
    assert main([before, after, "--no-color"]) == 0


def test_exit_code_one_with_flag(env_files):
    before, after = env_files
    assert main([before, after, "--exit-code", "--no-color"]) == 1


def test_missing_file_returns_2(tmp_path):
    existing = tmp_path / "a.env"
    existing.write_text("X=1\n")
    assert main([str(existing), "/nonexistent/path.env"]) == 2


def test_json_output(env_files, capsys):
    before, after = env_files
    main([before, after, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "added" in data
    assert "ADDED" in data["added"]
    assert "REMOVED" in data["removed"]
    assert "CHANGED" in data["changed"]


def test_text_output_contains_symbols(env_files, capsys):
    before, after = env_files
    main([before, after, "--no-color"])
    captured = capsys.readouterr()
    assert "+" in captured.out
    assert "-" in captured.out
