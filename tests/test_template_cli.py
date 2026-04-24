"""Tests for envoy_diff.template_cli."""

import json
import os
import pytest
from argparse import Namespace
from envoy_diff.template_cli import cmd_template, build_template_parser


@pytest.fixture()
def env_files(tmp_path):
    template = tmp_path / "template.env"
    template.write_text("DSN=postgres://${DB_HOST}:5432/app\nAPP=${APP_NAME}\n")

    context = tmp_path / "context.env"
    context.write_text("DB_HOST=db.prod.internal\nAPP_NAME=myservice\n")

    return str(template), str(context)


def _args(**kwargs):
    defaults = {"strict": False, "format": "text", "context": None}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_cmd_template_text_output(env_files, capsys):
    template_file, context_file = env_files
    rc = cmd_template(_args(template_file=template_file, context=context_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "DSN=postgres://db.prod.internal:5432/app" in out
    assert "APP=myservice" in out


def test_cmd_template_json_output(env_files, capsys):
    template_file, context_file = env_files
    rc = cmd_template(_args(template_file=template_file, context=context_file, format="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["rendered"]["DSN"] == "postgres://db.prod.internal:5432/app"
    assert data["substitutions"] == 2
    assert data["unresolved"] == []


def test_cmd_template_missing_template_returns_2(tmp_path):
    rc = cmd_template(_args(template_file=str(tmp_path / "ghost.env")))
    assert rc == 2


def test_cmd_template_missing_context_returns_2(env_files):
    template_file, _ = env_files
    rc = cmd_template(_args(template_file=template_file, context="/no/such/file.env"))
    assert rc == 2


def test_cmd_template_strict_mode_fails_on_unresolved(tmp_path):
    t = tmp_path / "t.env"
    t.write_text("KEY=${UNDEFINED_VAR}\n")
    rc = cmd_template(_args(template_file=str(t), strict=True))
    assert rc == 1


def test_cmd_template_strict_mode_passes_when_resolved(env_files):
    template_file, context_file = env_files
    rc = cmd_template(_args(template_file=template_file, context=context_file, strict=True))
    assert rc == 0


def test_cmd_template_no_context_uses_self_substitution(tmp_path, capsys):
    t = tmp_path / "self.env"
    t.write_text("HOST=localhost\nURL=http://${HOST}/api\n")
    rc = cmd_template(_args(template_file=str(t)))
    assert rc == 0
    out = capsys.readouterr().out
    assert "URL=http://localhost/api" in out
