"""CLI entry point for the template rendering command."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envoy_diff.parser import parse_env_file
from envoy_diff.templater import render_template


def build_template_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Render an env template by substituting variables from a context file."
    if parent is not None:
        parser = parent.add_parser("template", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envoy-template", description=description)

    parser.add_argument("template_file", help="Env file containing ${VAR} references")
    parser.add_argument(
        "--context",
        metavar="FILE",
        help="Env file to use as substitution context (defaults to template itself)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any variables remain unresolved",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser


def cmd_template(args: argparse.Namespace) -> int:
    try:
        template = parse_env_file(args.template_file)
    except FileNotFoundError:
        print(f"error: template file not found: {args.template_file}", file=sys.stderr)
        return 2

    context_path = getattr(args, "context", None)
    if context_path:
        try:
            context = parse_env_file(context_path)
        except FileNotFoundError:
            print(f"error: context file not found: {context_path}", file=sys.stderr)
            return 2
    else:
        context = dict(template)

    try:
        result = render_template(template, context, strict=args.strict)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        out = {
            "rendered": result.rendered,
            "substitutions": result.substitutions,
            "unresolved": result.unresolved,
        }
        print(json.dumps(out, indent=2))
    else:
        for key, value in result.rendered.items():
            print(f"{key}={value}")
        print(f"# {result.summary()}", file=sys.stderr)

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_template_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_template(args))


if __name__ == "__main__":
    main()
