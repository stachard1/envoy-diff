"""CLI entry point for the diff pipeline command."""
import argparse
import json
import sys
from pathlib import Path

from envoy_diff.parser import parse_env_file
from envoy_diff.transformer import TransformRule
from envoy_diff.differ_pipeline import build_pipeline
from envoy_diff.formatter import format_text, format_json


def _parse_rules(raw: list[str]) -> list[TransformRule]:
    rules = []
    for r in raw or []:
        parts = r.split(":", 2)
        if len(parts) < 2:
            raise ValueError(f"Invalid transform rule: {r!r}")
        op = parts[0]
        key = parts[1]
        value = parts[2] if len(parts) == 3 else ""
        rules.append(TransformRule(op=op, key=key, value=value))
    return rules


def build_pipeline_parser(parent: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    p = parent or argparse.ArgumentParser(prog="envoy-diff pipeline", description="Run a transformation pipeline then diff.")
    p.add_argument("before", help="Path to the 'before' env file")
    p.add_argument("after", help="Path to the 'after' env file")
    p.add_argument("--filter-prefix", metavar="PREFIX", help="Keep only keys with this prefix")
    p.add_argument("--filter-pattern", metavar="REGEX", help="Keep only keys matching this regex")
    p.add_argument("--transform", metavar="RULE", action="append", help="Transform rules (op:key[:value])")
    p.add_argument("--redact", action="store_true", help="Redact sensitive values before diff")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--fail-on-changes", action="store_true")
    return p


def run_pipeline(args: argparse.Namespace, out=sys.stdout) -> int:
    for path in (args.before, args.after):
        if not Path(path).exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2

    before = parse_env_file(args.before)
    after = parse_env_file(args.after)

    pipeline = build_pipeline()
    if getattr(args, "filter_prefix", None):
        pipeline.filter_prefix(args.filter_prefix)
    if getattr(args, "filter_pattern", None):
        pipeline.filter_pattern(args.filter_pattern)
    if getattr(args, "transform", None):
        try:
            rules = _parse_rules(args.transform)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        pipeline.transform(rules)
    if getattr(args, "redact", False):
        pipeline.redact()

    result = pipeline.run(before, after)

    if args.format == "json":
        print(format_json(result.diff), file=out)
    else:
        print(format_text(result.diff), file=out)
        print(f"# {result.summary()}", file=out)

    if args.fail_on_changes and result.has_changes:
        return 1
    return 0


def main() -> None:
    parser = build_pipeline_parser()
    args = parser.parse_args()
    sys.exit(run_pipeline(args))


if __name__ == "__main__":
    main()
