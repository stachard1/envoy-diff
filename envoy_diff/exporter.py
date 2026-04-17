"""Export diff reports to various file formats."""
from __future__ import annotations

import json
import csv
import io
from pathlib import Path
from typing import Union

from envoy_diff.reporter import Report


def export_json(report: Report, path: Union[str, Path]) -> None:
    """Write the report as a JSON file."""
    data = {
        "summary": report.summary(),
        "has_issues": report.has_issues(),
        "diff": {
            "added": list(report.diff.added),
            "removed": list(report.diff.removed),
            "changed": [
                {"key": k, "before": v[0], "after": v[1]}
                for k, v in report.diff.changed.items()
            ],
            "unchanged": list(report.diff.unchanged),
        },
        "audit": {
            "sensitive_added": list(report.audit.sensitive_added),
            "sensitive_removed": list(report.audit.sensitive_removed),
            "sensitive_changed": list(report.audit.sensitive_changed),
        },
    }
    Path(path).write_text(json.dumps(data, indent=2))


def export_csv(report: Report, path: Union[str, Path]) -> None:
    """Write the diff portion of the report as a CSV file."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["change_type", "key", "before", "after", "sensitive"])

    sensitive_keys = (
        report.audit.sensitive_added
        | report.audit.sensitive_removed
        | report.audit.sensitive_changed
    )

    for key in sorted(report.diff.added):
        writer.writerow(["added", key, "", "", key in sensitive_keys])
    for key in sorted(report.diff.removed):
        writer.writerow(["removed", key, "", "", key in sensitive_keys])
    for key, (before, after) in sorted(report.diff.changed.items()):
        writer.writerow(["changed", key, before, after, key in sensitive_keys])

    Path(path).write_text(buf.getvalue())


def export_report(report: Report, path: Union[str, Path], fmt: str = "json") -> None:
    """Dispatch export to the requested format."""
    fmt = fmt.lower()
    if fmt == "json":
        export_json(report, path)
    elif fmt == "csv":
        export_csv(report, path)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}")
