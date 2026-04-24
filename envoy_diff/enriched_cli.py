"""CLI entry point for the enriched diff command."""

import argparse
import json
import sys
from typing import List, Optional

from envoy_diff.parser import parse_env_file
from envoy_diff.differ_annotated import enrich_diff


def build_enriched_parser(sub=None) -> argparse.ArgumentParser:
    description = "Diff two env files with annotations, risk scoring, and audit."
    if sub is not None:
        parser = sub.add_parser("enrich", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy-enrich", description=description)
    parser.add_argument("before", help="Path to the baseline env file")
    parser.add_argument("after", help="Path to the updated env file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with code 1 if audit findings are present",
    )
    parser.add_argument(
        "--fail-on-score",
        type=int,
        default=None,
        metavar="THRESHOLD",
        help="Exit with code 1 if risk score meets or exceeds THRESHOLD",
    )
    return parser


def run_enriched(args: argparse.Namespace, out=sys.stdout) -> int:
    try:
        before = parse_env_file(args.before)
    except FileNotFoundError:
        print(f"error: file not found: {args.before}", file=sys.stderr)
        return 2
    try:
        after = parse_env_file(args.after)
    except FileNotFoundError:
        print(f"error: file not found: {args.after}", file=sys.stderr)
        return 2

    result = enrich_diff(before, after)

    if args.format == "json":
        print(json.dumps(result.as_dict(), indent=2), file=out)
    else:
        print(result.summary(), file=out)

    if args.fail_on_findings and result.has_findings:
        return 1
    if args.fail_on_score is not None and result.score.value >= args.fail_on_score:
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_enriched_parser()
    args = parser.parse_args(argv)
    sys.exit(run_enriched(args))


if __name__ == "__main__":
    main()
