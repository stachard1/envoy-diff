import json
import pytest
from io import StringIO
from pathlib import Path
from argparse import Namespace
from envoy_diff.score_cli import run_score, build_score_parser


@pytest.fixture
def env_files(tmp_path):
    before = tmp_path / "before.env"
    after = tmp_path / "after.env"
    before.write_text("APP=myapp\nDB_PASSWORD=secret\n")
    after.write_text("APP=myapp\nDB_PASSWORD=newsecret\nNEW_KEY=value\n")
    return str(before), str(after)


def _args(before, after, as_json=False, fail_on=None):
    return Namespace(before=before, after=after, as_json=as_json, fail_on=fail_on)


def test_run_score_text_output(env_files):
    before, after = env_files
    out = StringIO()
    code = run_score(_args(before, after), out=out)
    text = out.getvalue()
    assert "Risk level" in text
    assert "Risk score" in text
    assert code == 0


def test_run_score_json_output(env_files):
    before, after = env_files
    out = StringIO()
    run_score(_args(before, after, as_json=True), out=out)
    data = json.loads(out.getvalue())
    assert "total" in data
    assert "level" in data
    assert "breakdown" in data


def test_fail_on_low_exits_one_when_changes(env_files):
    before, after = env_files
    out = StringIO()
    code = run_score(_args(before, after, fail_on="low"), out=out)
    assert code == 1


def test_fail_on_high_exits_zero_for_low_risk(tmp_path):
    before = tmp_path / "b.env"
    after = tmp_path / "a.env"
    before.write_text("X=1\n")
    after.write_text("X=1\nY=2\n")
    out = StringIO()
    code = run_score(_args(str(before), str(after), fail_on="high"), out=out)
    assert code == 0


def test_missing_file_returns_2(tmp_path):
    out = StringIO()
    code = run_score(_args("missing.env", "also_missing.env"), out=out)
    assert code == 2


def test_no_changes_score_level_none(tmp_path):
    f = tmp_path / "env"
    f.write_text("A=1\n")
    out = StringIO()
    run_score(_args(str(f), str(f), as_json=True), out=out)
    data = json.loads(out.getvalue())
    assert data["level"] == "none"
    assert data["total"] == 0


def test_build_score_parser_standalone():
    p = build_score_parser()
    args = p.parse_args(["before.env", "after.env", "--fail-on", "medium"])
    assert args.fail_on == "medium"
    assert args.before == "before.env"
