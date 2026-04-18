"""CLI for merging multiple env files."""
import argparse
import json
import sys
from typing import List

from envoy_diff.parser import parse_env_file
from envoy_diff.merger import merge_envs


def build_merge_parser(parent=None) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envoy-diff merge",
        description="Merge multiple .env files into one.",
        parents=[parent] if parent else [],
        add_help=parent is None,
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="env files to merge")
    p.add_argument(
        "--strategy",
        choices=["last", "first", "error"],
        default="last",
        help="conflict resolution strategy (default: last)",
    )
    p.add_argument(
        "--json", dest="as_json", action="store_true", help="output as JSON"
    )
    p.add_argument(
        "--fail-on-conflict",
        action="store_true",
        help="exit with code 1 if conflicts are found",
    )
    return p


def run_merge(args: argparse.Namespace, out=sys.stdout) -> int:
    envs = []
    for path in args.files:
        try:
            envs.append(parse_env_file(path))
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2

    result = merge_envs(*envs, strategy=args.strategy, labels=args.files)

    if args.as_json:
        payload = {
            "merged": result.merged,
            "conflicts": [
                {"key": c.key, "values": c.values} for c in result.conflicts
            ],
        }
        print(json.dumps(payload, indent=2), file=out)
    else:
        for key, value in sorted(result.merged.items()):
            print(f"{key}={value}", file=out)
        if result.has_conflicts():
            print("", file=out)
            print("# Conflicts:", file=out)
            for c in result.conflicts:
                print(f"#   {c}", file=out)

    if args.fail_on_conflict and result.has_conflicts():
        return 1
    return 0


def main(argv=None):
    parser = build_merge_parser()
    args = parser.parse_args(argv)
    sys.exit(run_merge(args))


if __name__ == "__main__":
    main()
