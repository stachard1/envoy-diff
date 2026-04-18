"""CLI integration for diffing two env files with optional audit and redaction."""

import argparse
import sys

from envoy_diff.parser import parse_env_file
from envoy_diff.differ import diff_envs
from envoy_diff.formatter import format_text, format_json
from envoy_diff.auditor import audit_diff
from envoy_diff.redactor import redact_diff


def build_diff_parser(parent=None):
    if parent is None:
        parser = argparse.ArgumentParser(prog="envoy-diff", description="Diff two .env files")
    else:
        parser = parent

    parser.add_argument("file_a", help="Base env file")
    parser.add_argument("file_b", help="Target env file")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--audit", action="store_true", help="Show audit findings for sensitive keys")
    parser.add_argument("--redact", action="store_true", help="Redact sensitive values in output")
    parser.add_argument("--exit-code", action="store_true", help="Exit 1 if differences found")
    return parser


def run_diff(args):
    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    result = diff_envs(env_a, env_b)

    diff_to_render = result
    if args.redact:
        from envoy_diff.differ import EnvDiffResult
        redacted = redact_diff(result)
        diff_to_render = redacted

    if args.format == "json":
        print(format_json(diff_to_render))
    else:
        print(format_text(diff_to_render))

    if args.audit:
        audit = audit_diff(result)
        if audit.has_findings():
            print("\n[audit] " + audit.summary())

    if args.exit_code and result.has_changes():
        return 1
    return 0


def main():
    parser = build_diff_parser()
    args = parser.parse_args()
    sys.exit(run_diff(args))


if __name__ == "__main__":
    main()
