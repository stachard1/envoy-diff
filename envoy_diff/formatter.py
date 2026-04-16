"""Output formatters for env diff results."""
from typing import TextIO
import sys
from envoy_diff.differ import EnvDiffResult


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_text(result: EnvDiffResult, use_color: bool = True, out: TextIO = sys.stdout) -> None:
    """Print a human-readable diff to `out`."""
    if not result.has_changes():
        out.write("No changes detected.\n")
        return

    for key in sorted(result.added):
        line = f"+ {key}={result.added[key]}"
        out.write(_colorize(line, ANSI_GREEN, use_color) + "\n")

    for key in sorted(result.removed):
        line = f"- {key}={result.removed[key]}"
        out.write(_colorize(line, ANSI_RED, use_color) + "\n")

    for key in sorted(result.changed):
        old_val, new_val = result.changed[key]
        out.write(_colorize(f"~ {key}={old_val}", ANSI_RED, use_color) + "\n")
        out.write(_colorize(f"~ {key}={new_val}", ANSI_GREEN, use_color) + "\n")


def format_json(result: EnvDiffResult, out: TextIO = sys.stdout) -> None:
    """Print a JSON representation of the diff to `out`."""
    import json

    data = {
        "added": result.added,
        "removed": result.removed,
        "changed": {
            k: {"old": v[0], "new": v[1]} for k, v in result.changed.items()
        },
        "unchanged_count": len(result.unchanged),
        "summary": result.summary(),
    }
    out.write(json.dumps(data, indent=2) + "\n")
