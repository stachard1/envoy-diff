"""Command-line interface for envoy-diff."""
import argparse
import sys
from envoy_diff.parser import parse_env_file
from envoy_diff.differ import diff_envs
from envoy_diff.formatter import format_text, format_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envoy-diff",
        description="Diff and audit environment variable changes across deployments.",
    )
    p.add_argument("before", help="Path to the 'before' .env file")
    p.add_argument("after", help="Path to the 'after' .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if there are any changes",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        before = parse_env_file(args.before)
        after = parse_env_file(args.after)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(before, after)

    if args.format == "json":
        format_json(result)
    else:
        format_text(result, use_color=not args.no_color)

    if args.exit_code and result.has_changes():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
