import json
import pytest
from pathlib import Path
from argparse import Namespace
from envoy_diff.transform_cli import cmd_transform, build_transform_parser


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nAPP_ENV=staging\nDEBUG=true\n")
    return str(f)


def _args(env_file, rules, fmt="text"):
    return Namespace(file=env_file, rules=json.dumps(rules), format=fmt, func=cmd_transform)


def test_cmd_transform_text_output(env_file, capsys):
    args = _args(env_file, [{"key_pattern": "DEBUG", "action": "delete"}])
    rc = cmd_transform(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "DEBUG" not in out
    assert "DB_HOST=localhost" in out


def test_cmd_transform_json_output(env_file, capsys):
    args = _args(env_file, [{"key_pattern": "APP_ENV", "action": "set", "target": "production"}], fmt="json")
    rc = cmd_transform(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["env"]["APP_ENV"] == "production"
    assert any("set:APP_ENV" in a for a in data["applied"])


def test_cmd_transform_rename(env_file, capsys):
    args = _args(env_file, [{"key_pattern": "DB_HOST", "action": "rename", "target": "DATABASE_HOST"}], fmt="json")
    rc = cmd_transform(args)
    data = json.loads(capsys.readouterr().out)
    assert "DATABASE_HOST" in data["env"]
    assert "DB_HOST" not in data["env"]


def test_missing_file_returns_2(tmp_path, capsys):
    args = _args(str(tmp_path / "missing.env"), [])
    rc = cmd_transform(args)
    assert rc == 2


def test_build_transform_parser():
    parser = build_transform_parser()
    args = parser.parse_args(["some.env", "--rules", "[]", "--format", "json"])
    assert args.format == "json"
    assert args.file == "some.env"
