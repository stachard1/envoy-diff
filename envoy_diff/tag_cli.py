"""CLI subcommand for tagging and inspecting env variable categories."""

import argparse
import json
import sys
from typing import List

from envoy_diff.parser import parse_env_file
from envoy_diff.tagger import tag_env, tags_summary


def cmd_tag(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2

    tagged = tag_env(env)
    summary = tags_summary(tagged)

    if args.format == "json":
        payload = {
            "file": args.env_file,
            "tags": {tag: keys for tag, keys in summary.items()},
            "per_key": {k: sorted(v) for k, v in tagged.tags.items() if v},
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not summary:
        print("No tags found.")
        return 0

    if args.key:
        key_tags = tagged.get_tags(args.key)
        if key_tags:
            print(f"{args.key}: {', '.join(sorted(key_tags))}")
        else:
            print(f"{args.key}: (no tags)")
        return 0

    for tag, keys in summary.items():
        print(f"[{tag}]")
        for k in keys:
            print(f"  {k}")

    return 0


def build_tag_parser(subparsers=None):
    desc = "Tag and categorize environment variables"
    if subparsers is not None:
        p = subparsers.add_parser("tag", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envoy-tag", description=desc)
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--key", default=None, help="Show tags for a specific key")
    p.set_defaults(func=cmd_tag)
    return p


def main(argv: List[str] | None = None) -> None:
    parser = build_tag_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_tag(args))


if __name__ == "__main__":
    main()
