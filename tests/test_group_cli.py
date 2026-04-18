import json
import pytest
from pathlib import Path
from unittest.mock import patch
from envoy_diff.group_cli import cmd_group, build_group_parser


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=envoy\nSECRET_KEY=abc\nLOG_LEVEL=info\n"
    )
    return str(f)


def _args(env_file, by="prefix", fmt="text"):
    p = build_group_parser()
    return p.parse_args([env_file, "--by", by, "--format", fmt])


def test_cmd_group_text_output(env_file, capsys):
    rc = cmd_group(_args(env_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB" in out
    assert "APP" in out


def test_cmd_group_json_output(env_file, capsys):
    rc = cmd_group(_args(env_file, fmt="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "DB" in data
    assert isinstance(data["DB"], list)


def test_cmd_group_by_tag(env_file, capsys):
    rc = cmd_group(_args(env_file, by="tag"))
    assert rc == 0
    out = capsys.readouterr().out
    assert len(out) > 0


def test_cmd_group_missing_file(tmp_path, capsys):
    p = build_group_parser()
    args = p.parse_args([str(tmp_path / "missing.env")])
    rc = cmd_group(args)
    assert rc == 2
    assert "not found" in capsys.readouterr().err


def test_cmd_group_json_contains_keys(env_file, capsys):
    cmd_group(_args(env_file, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    all_keys = [k for keys in data.values() for k in keys]
    assert "DB_HOST" in all_keys
    assert "DB_PORT" in all_keys


def test_build_group_parser_defaults(env_file):
    p = build_group_parser()
    args = p.parse_args([env_file])
    assert args.by == "prefix"
    assert args.format == "text"
