"""Tests for the enriched diff module."""

import json
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from envoy_diff.differ_annotated import enrich_diff, EnrichedDiff
from envoy_diff.enriched_cli import run_enriched


BEFORE = {
    "APP_ENV": "production",
    "DB_PASSWORD": "secret123",
    "LOG_LEVEL": "info",
}

AFTER = {
    "APP_ENV": "staging",
    "DB_PASSWORD": "newsecret",
    "NEW_KEY": "hello",
}


@pytest.fixture()
def enriched():
    return enrich_diff(BEFORE, AFTER)


def test_enrich_diff_returns_enriched_diff(enriched):
    assert isinstance(enriched, EnrichedDiff)


def test_has_changes_when_envs_differ(enriched):
    assert enriched.has_changes is True


def test_no_changes_when_envs_identical():
    result = enrich_diff(BEFORE, BEFORE)
    assert result.has_changes is False


def test_score_is_nonzero_for_sensitive_changes(enriched):
    assert enriched.score.value > 0


def test_audit_finds_sensitive_key(enriched):
    assert enriched.has_findings is True


def test_sensitive_changes_includes_password(enriched):
    sensitive_keys = [k.key for k in enriched.annotated.sensitive_changes()]
    assert "DB_PASSWORD" in sensitive_keys


def test_summary_contains_risk_score(enriched):
    s = enriched.summary()
    assert "Risk score" in s


def test_summary_contains_change_counts(enriched):
    s = enriched.summary()
    assert "added=1" in s
    assert "removed=1" in s


def test_as_dict_has_expected_keys(enriched):
    d = enriched.as_dict()
    for key in ("risk_score", "risk_level", "added", "removed", "changed", "sensitive_changes", "audit_findings"):
        assert key in d


def test_as_dict_added_contains_new_key(enriched):
    assert "NEW_KEY" in enriched.as_dict()["added"]


def test_as_dict_removed_contains_log_level(enriched):
    assert "LOG_LEVEL" in enriched.as_dict()["removed"]


# --- CLI tests ---


def _args(**kwargs):
    defaults = {
        "before": "a.env",
        "after": "b.env",
        "format": "text",
        "fail_on_findings": False,
        "fail_on_score": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_run_enriched_text_output(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("APP_ENV=production\nDB_PASSWORD=secret\n")
    b.write_text("APP_ENV=staging\nDB_PASSWORD=newsecret\n")
    out = StringIO()
    code = run_enriched(_args(before=str(a), after=str(b)), out=out)
    assert code == 0
    assert "Risk score" in out.getvalue()


def test_run_enriched_json_output(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("APP_ENV=production\n")
    b.write_text("APP_ENV=staging\n")
    out = StringIO()
    code = run_enriched(_args(before=str(a), after=str(b), format="json"), out=out)
    assert code == 0
    data = json.loads(out.getvalue())
    assert "risk_score" in data


def test_fail_on_findings_returns_one(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("DB_PASSWORD=old\n")
    b.write_text("DB_PASSWORD=new\n")
    out = StringIO()
    code = run_enriched(_args(before=str(a), after=str(b), fail_on_findings=True), out=out)
    assert code == 1


def test_missing_before_file_returns_2(tmp_path):
    b = tmp_path / "b.env"
    b.write_text("KEY=val\n")
    out = StringIO()
    code = run_enriched(_args(before="/no/such/file.env", after=str(b)), out=out)
    assert code == 2


def test_fail_on_score_threshold(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("API_SECRET=old\nDB_TOKEN=x\n")
    b.write_text("API_SECRET=new\nDB_TOKEN=y\n")
    out = StringIO()
    code = run_enriched(_args(before=str(a), after=str(b), fail_on_score=1), out=out)
    assert code == 1
