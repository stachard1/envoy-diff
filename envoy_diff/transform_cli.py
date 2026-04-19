"""CLI for applying transformations to an env file."""
from __future__ import annotations
import argparse
import json
import sys
from envoy_diff.parser import parse_env_file
from envoy_diff.transformer import TransformRule, apply_transforms


def _parse_rules(rules_json: str) -> list[TransformRule]:
    raw = json.loads(rules_json)
    result = []
    for r in raw:
        result.append(TransformRule(
            key_pattern=r["key_pattern"],
            action=r["action"],
            target=r.get("target"),
            value_map=r.get("value_map"),
        ))
    return result


def cmd_transform(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    rules = _parse_rules(args.rules)
    result = apply_transforms(env, rules)

    if args.format == "json":
        print(json.dumps({"env": result.env, "applied": result.applied, "skipped": result.skipped}, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")
        if result.applied:
            print(f"\n# Applied: {', '.join(result.applied)}", file=sys.stderr)

    return 0


def build_transform_parser(sub=None):
    if sub is None:
        parser = argparse.ArgumentParser(description="Transform env file keys/values")
    else:
        parser = sub.add_parser("transform", help="Transform env file")
    parser.add_argument("file", help="Env file to transform")
    parser.add_argument("--rules", required=True, help="JSON array of transform rules")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.set_defaults(func=cmd_transform)
    return parser


def main():
    parser = build_transform_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
