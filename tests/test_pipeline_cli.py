"""Tests for pipeline_cli.py"""
import json
import pytest
from pathlib import Path
from argparse import Namespace
from io import StringIO

from envoy_diff.pipeline_cli import build_pipeline_parser, run_pipeline


@pytest.fixture
def env_files(tmp_path):
    before = tmp_path / "before.env"
    after = tmp_path / "after.env"
    before.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_SECRET=old\nLOG_LEVEL=info\n")
    after.write_text("DB_HOST=prod-db\nDB_PORT=5432\nAPP_SECRET=new\nLOG_LEVEL=warn\n")
    return str(before), str(after)


def _args(before, after, **kwargs) -> Namespace:
    defaults = dict(
        before=before, after=after,
        filter_prefix=None, filter_pattern=None,
        transform=None, redact=False,
        format="text", fail_on_changes=False
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_run_pipeline_text_output(env_files):
    before, after = env_files
    out = StringIO()
    code = run_pipeline(_args(before, after), out=out)
    assert code == 0
    text = out.getvalue()
    assert "DB_HOST" in text


def test_run_pipeline_json_output(env_files):
    before, after = env_files
    out = StringIO()
    code = run_pipeline(_args(before, after, format="json"), out=out)
    assert code == 0
    data = json.loads(out.getvalue())
    assert "changed" in data or isinstance(data, dict)


def test_fail_on_changes_returns_one(env_files):
    before, after = env_files
    out = StringIO()
    code = run_pipeline(_args(before, after, fail_on_changes=True), out=out)
    assert code == 1


def test_no_changes_returns_zero(tmp_path):
    f = tmp_path / "env"
    f.write_text("KEY=value\n")
    out = StringIO()
    code = run_pipeline(_args(str(f), str(f), fail_on_changes=True), out=out)
    assert code == 0


def test_missing_file_returns_2(env_files):
    before, _ = env_files
    out = StringIO()
    code = run_pipeline(_args(before, "/no/such/file.env"), out=out)
    assert code == 2


def test_filter_prefix_in_output(env_files):
    before, after = env_files
    out = StringIO()
    run_pipeline(_args(before, after, filter_prefix="DB_"), out=out)
    text = out.getvalue()
    assert "APP_SECRET" not in text


def test_invalid_transform_rule_returns_2(env_files):
    before, after = env_files
    out = StringIO()
    code = run_pipeline(_args(before, after, transform=["badrule"]), out=out)
    assert code == 2


def test_build_pipeline_parser_returns_parser():
    p = build_pipeline_parser()
    assert p is not None
    args = p.parse_args(["a.env", "b.env"])
    assert args.before == "a.env"
