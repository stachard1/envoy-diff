"""CLI commands for filtering environment variables."""
from __future__ import annotations
import argparse
import json
import sys
from envoy_diff.parser import parse_env_file
from envoy_diff.filter import filter_env


def cmd_filter(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    result = filter_env(
        env,
        prefix=getattr(args, "prefix", None),
        pattern=getattr(args, "pattern", None),
        tag=getattr(args, "tag", None),
    )

    if args.format == "json":
        print(json.dumps({"matched": result.matched, "excluded_count": len(result.excluded)}, indent=2))
    else:
        if not result.matched:
            print("No keys matched.")
        else:
            for k, v in sorted(result.matched.items()):
                print(f"  {k}={v}")
        print(f"\n{result.count} key(s) matched, {len(result.excluded)} excluded.")
    return 0


def build_filter_parser(sub=None):
    if sub is None:
        parser = argparse.ArgumentParser(description="Filter env vars")
    else:
        parser = sub.add_parser("filter", help="Filter environment variables")
    parser.add_argument("file", help="Path to .env file")
    parser.add_argument("--prefix", help="Filter by key prefix")
    parser.add_argument("--pattern", help="Filter by regex pattern on key names")
    parser.add_argument("--tag", help="Filter by tag (sensitive, database, network, ...)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.set_defaults(func=cmd_filter)
    return parser


def main():
    parser = build_filter_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
