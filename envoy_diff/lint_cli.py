"""CLI commands for linting environment files."""
import argparse
import sys
from envoy_diff.parser import parse_env_file
from envoy_diff.linter import lint_env, errors, warnings, summary, has_issues

def cmd_lint(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    result = lint_env(env, allow_lowercase=args.allow_lowercase)

    if not has_issues(result):
        print("No lint issues found.")
        return 0

    for issue in errors(result):
        print(f"  ERROR   [{issue.key}] {issue.message}")
    for issue in warnings(result):
        print(f"  WARNING [{issue.key}] {issue.message}")

    print(f"\n{summary(result)}")

    if args.strict and errors(result):
        return 1
    if args.warnings_as_errors and has_issues(result):
        return 1
    if errors(result):
        return 1
    return 0

def build_lint_parser(subparsers=None):
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="envoy-lint", description="Lint an env file")
    else:
        parser = subparsers.add_parser("lint", help="Lint an env file")

    parser.add_argument("file", help="Path to .env file")
    parser.add_argument("--allow-lowercase", action="store_true", default=False,
                        help="Allow lowercase keys without warning")
    parser.add_argument("--strict", action="store_true", default=False,
                        help="Exit 1 on any error")
    parser.add_argument("--warnings-as-errors", action="store_true", default=False,
                        help="Treat warnings as errors")
    parser.set_defaults(func=cmd_lint)
    return parser

def main():
    parser = build_lint_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))

if __name__ == "__main__":
    main()
