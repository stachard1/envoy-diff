"""Tests for envoy_diff.exporter."""
import json
import csv
import pytest
from pathlib import Path

from envoy_diff.differ import diff_envs
from envoy_diff.reporter import generate_report
from envoy_diff.exporter import export_json, export_csv, export_report


@pytest.fixture()
def report():
    before = {"DB_HOST": "localhost", "SECRET_KEY": "old", "PORT": "8080"}
    after = {"DB_HOST": "prod-db", "SECRET_KEY": "new", "TIMEOUT": "30"}
    return generate_report(before, after)


def test_export_json_creates_file(report, tmp_path):
    out = tmp_path / "report.json"
    export_json(report, out)
    assert out.exists()


def test_export_json_structure(report, tmp_path):
    out = tmp_path / "report.json"
    export_json(report, out)
    data = json.loads(out.read_text())
    assert "diff" in data
    assert "audit" in data
    assert "summary" in data
    assert "has_issues" in data


def test_export_json_diff_contents(report, tmp_path):
    out = tmp_path / "report.json"
    export_json(report, out)
    data = json.loads(out.read_text())
    assert "TIMEOUT" in data["diff"]["added"]
    assert "PORT" in data["diff"]["removed"]
    changed_keys = [c["key"] for c in data["diff"]["changed"]]
    assert "DB_HOST" in changed_keys


def test_export_csv_creates_file(report, tmp_path):
    out = tmp_path / "report.csv"
    export_csv(report, out)
    assert out.exists()


def test_export_csv_rows(report, tmp_path):
    out = tmp_path / "report.csv"
    export_csv(report, out)
    rows = list(csv.DictReader(out.read_text().splitlines()))
    change_types = {r["change_type"] for r in rows}
    assert "added" in change_types
    assert "removed" in change_types
    assert "changed" in change_types


def test_export_csv_sensitive_flag(report, tmp_path):
    out = tmp_path / "report.csv"
    export_csv(report, out)
    rows = list(csv.DictReader(out.read_text().splitlines()))
    sensitive_rows = [r for r in rows if r["key"] == "SECRET_KEY"]
    assert sensitive_rows
    assert sensitive_rows[0]["sensitive"] == "True"


def test_export_report_dispatch_json(report, tmp_path):
    out = tmp_path / "out.json"
    export_report(report, out, fmt="json")
    assert out.exists()


def test_export_report_dispatch_csv(report, tmp_path):
    out = tmp_path / "out.csv"
    export_report(report, out, fmt="csv")
    assert out.exists()


def test_export_report_unknown_format(report, tmp_path):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_report(report, tmp_path / "out.xml", fmt="xml")
