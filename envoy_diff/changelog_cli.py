"""CLI command for generating a changelog from multiple env file pairs."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.parser import parse_env_file
from envoy_diff.differ_changelog import build_changelog, Changelog


def _changelog_as_dict(changelog: Changelog) -> dict:
    return {
        "summary": changelog.summary(),
        "total": changelog.total_entries,
        "entries": [
            {
                "label": e.label,
                "timestamp": e.timestamp,
                "has_changes": e.has_changes,
                "risk_level": e.risk_level,
                "sensitive_keys": e.sensitive_keys,
                "added": list(e.diff.added),
                "removed": list(e.diff.removed),
                "changed": list(e.diff.changed.keys()),
            }
            for e in changelog.entries
        ],
    }


def cmd_changelog(args: argparse.Namespace) -> int:
    pairs: List[tuple[str, str]] = args.pairs
    if len(pairs) % 2 != 0:
        print("error: pairs must be provided as LABEL BEFORE AFTER triplets", file=sys.stderr)
        return 2

    snapshots = []
    i = 0
    while i < len(pairs):
        label, before_path, after_path = pairs[i], pairs[i + 1], pairs[i + 2]
        try:
            before = parse_env_file(before_path)
            after = parse_env_file(after_path)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        snapshots.append((label, before, after))
        i += 3

    changelog = build_changelog(snapshots)

    if args.format == "json":
        print(json.dumps(_changelog_as_dict(changelog), indent=2))
    else:
        print(changelog.summary())
        for entry in changelog.entries:
            print(f"  {entry.summary()}")

    return 0


def build_changelog_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser("changelog", help="Generate a changelog from env file pairs")
    p.add_argument(
        "pairs",
        nargs="+",
        metavar="LABEL|FILE",
        help="Triplets of LABEL BEFORE AFTER env files",
    )
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_changelog)
    return p


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="envoy-changelog")
    sub = parser.add_subparsers(dest="command")
    build_changelog_parser(sub)
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
