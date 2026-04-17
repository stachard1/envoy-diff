"""Tests for envoy_diff.reporter."""

import json
import pytest

from envoy_diff.reporter import generate_report, render_report_text, render_report_json, Report


@pytest.fixture
def clean_envs():
    before = {"HOST": "localhost", "PORT": "8080"}
    after = {"HOST": "localhost", "PORT": "9090"}
    return before, after


@pytest.fixture
def sensitive_envs():
    before = {"DB_PASSWORD": "old_pass", "HOST": "localhost"}
    after = {"DB_PASSWORD": "new_pass", "HOST": "remotehost"}
    return before, after


def test_generate_report_returns_report(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after)
    assert isinstance(report, Report)


def test_report_has_diff(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after)
    assert "PORT" in report.diff.changed


def test_report_no_sensitive_findings(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after)
    assert not report.has_issues


def test_report_sensitive_findings(sensitive_envs):
    before, after = sensitive_envs
    report = generate_report(before, after)
    assert report.has_issues


def test_summary_contains_title(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after, title="My Report")
    assert "My Report" in report.summary


def test_summary_no_findings_message(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after)
    assert "no sensitive" in report.summary


def test_render_text_contains_title(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after, title="TextReport")
    text = render_report_text(report, color=False)
    assert "TextReport" in text


def test_render_text_sensitive_shows_finding(sensitive_envs):
    before, after = sensitive_envs
    report = generate_report(before, after)
    text = render_report_text(report, color=False)
    assert "SENSITIVE" in text


def test_render_json_valid(clean_envs):
    before, after = clean_envs
    report = generate_report(before, after)
    data = json.loads(render_report_json(report))
    assert "diff" in data
    assert "audit" in data
    assert "title" in data


def test_render_json_audit_findings(sensitive_envs):
    before, after = sensitive_envs
    report = generate_report(before, after)
    data = json.loads(render_report_json(report))
    assert data["audit"]["has_findings"] is True
    assert len(data["audit"]["findings"]) > 0
