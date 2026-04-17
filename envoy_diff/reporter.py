"""Report generation for envoy-diff: combine diff and audit results into a structured report."""

from dataclasses import dataclass, field
from typing import Optional
import json

from .differ import EnvDiffResult, diff_envs
from .auditor import AuditResult, audit_diff
from .formatter import format_text, format_json


@dataclass
class Report:
    diff: EnvDiffResult
    audit: AuditResult
    title: str = "Environment Diff Report"

    @property
    def has_issues(self) -> bool:
        return self.audit.has_findings

    @property
    def summary(self) -> str:
        lines = [self.title]
        lines.append(self.diff.summary)
        if self.audit.has_findings:
            lines.append(self.audit.summary)
        else:
            lines.append("Audit: no sensitive changes detected.")
        return "\n".join(lines)


def generate_report(before: dict, after: dict, title: str = "Environment Diff Report") -> Report:
    """Generate a combined diff + audit report from two env dicts."""
    diff = diff_envs(before, after)
    audit = audit_diff(diff)
    return Report(diff=diff, audit=audit, title=title)


def render_report_text(report: Report, color: bool = True) -> str:
    """Render report as human-readable text."""
    sections = []
    sections.append(f"=== {report.title} ===")
    sections.append(format_text(report.diff, color=color))
    if report.audit.has_findings:
        sections.append("--- Audit Findings ---")
        for finding in report.audit.findings:
            sections.append(f"  [SENSITIVE] {finding}")
    return "\n".join(sections)


def render_report_json(report: Report) -> str:
    """Render report as JSON string."""
    diff_data = json.loads(format_json(report.diff))
    data = {
        "title": report.title,
        "diff": diff_data,
        "audit": {
            "has_findings": report.audit.has_findings,
            "findings": report.audit.findings,
            "summary": report.audit.summary,
        },
    }
    return json.dumps(data, indent=2)
