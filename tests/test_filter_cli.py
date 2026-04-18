"""Tests for envoy_diff.filter_cli."""
import json
import pytest
from unittest.mock import patch
from argparse import Namespace
from envoy_diff.filter_cli import cmd_filter, build_filter_parser


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PASSWORD=secret\nAPP_PORT=8080\nLOG_LEVEL=info\n")
    return str(f)


def _args(**kwargs):
    defaults = {"prefix": None, "pattern": None, "tag": None, "format": "text"}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_cmd_filter_text_output(env_file, capsys):
    args = _args(file=env_file, prefix="DB")
    code = cmd_filter(args)
    out = capsys.readouterr().out
    assert code == 0
    assert "DB_HOST" in out
    assert "APP_PORT" not in out


def test_cmd_filter_json_output(env_file, capsys):
    args = _args(file=env_file, prefix="DB", format="json")
    code = cmd_filter(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DB_HOST" in data["matched"]
    assert "excluded_count" in data


def test_cmd_filter_by_tag(env_file, capsys):
    args = _args(file=env_file, tag="sensitive")
    code = cmd_filter(args)
    out = capsys.readouterr().out
    assert code == 0
    assert "DB_PASSWORD" in out


def test_cmd_filter_no_match(env_file, capsys):
    args = _args(file=env_file, prefix="XYZ")
    code = cmd_filter(args)
    out = capsys.readouterr().out
    assert "No keys matched" in out
    assert code == 0


def test_missing_file_returns_2(tmp_path, capsys):
    args = _args(file=str(tmp_path / "missing.env"))
    code = cmd_filter(args)
    assert code == 2


def test_build_filter_parser_returns_parser():
    parser = build_filter_parser()
    args = parser.parse_args(["somefile.env", "--prefix", "APP"])
    assert args.prefix == "APP"
    assert args.file == "somefile.env"
