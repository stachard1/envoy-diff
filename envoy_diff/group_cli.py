"""CLI for grouping and displaying environment variable structure."""
from __future__ import annotations
import argparse
import sys
from envoy_diff.parser import parse_env_file
from envoy_diff.grouper import group_by_prefix, group_by_tag, group_summary


def cmd_group(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    if args.by == "tag":
        groups = group_by_tag(env)
    else:
        groups = group_by_prefix(env)

    if args.format == "json":
        import json
        data = {name: sorted(grp.keys) for name, grp in groups.items()}
        print(json.dumps(data, indent=2))
    else:
        print(group_summary(groups))

    return 0


def build_group_parser(sub=None):
    desc = "Group environment variables by prefix or tag"
    if sub is not None:
        p = sub.add_parser("group", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envoy-group", description=desc)
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--by",
        choices=["prefix", "tag"],
        default="prefix",
        help="Grouping strategy (default: prefix)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def main():
    p = build_group_parser()
    args = p.parse_args()
    sys.exit(cmd_group(args))


if __name__ == "__main__":
    main()
