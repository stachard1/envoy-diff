"""CLI commands for comparing profiles and snapshots."""
import argparse
import json
import sys

from envoy_diff.comparator import compare_profiles, compare_snapshots
from envoy_diff.formatter import format_json


def cmd_compare_profiles(args: argparse.Namespace) -> int:
    result = compare_profiles(args.profile_a, args.profile_b, args.profile_dir)
    if args.format == "json":
        data = {
            "label_a": result.label_a,
            "label_b": result.label_b,
            "diff": format_json(result.diff),
            "risk_level": result.score.level,
            "risk_score": result.score.total,
            "sensitive_findings": [f.key for f in result.audit.findings],
        }
        print(json.dumps(data, indent=2))
    else:
        print(result.summary())
    return 1 if (args.fail_on_change and result.diff.has_changes()) else 0


def cmd_compare_snapshots(args: argparse.Namespace) -> int:
    result = compare_snapshots(args.snapshot_a, args.snapshot_b)
    if args.format == "json":
        data = {
            "label_a": result.label_a,
            "label_b": result.label_b,
            "diff": format_json(result.diff),
            "risk_level": result.score.level,
            "risk_score": result.score.total,
            "sensitive_findings": [f.key for f in result.audit.findings],
        }
        print(json.dumps(data, indent=2))
    else:
        print(result.summary())
    return 1 if (args.fail_on_change and result.diff.has_changes()) else 0


def build_comparator_parser(subparsers=None):
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="envoy-compare")
        sub = parser.add_subparsers(dest="command")
    else:
        sub = subparsers

    p_prof = sub.add_parser("profiles", help="Compare two saved profiles")
    p_prof.add_argument("profile_a")
    p_prof.add_argument("profile_b")
    p_prof.add_argument("--profile-dir", default=".envoy_profiles")
    p_prof.add_argument("--format", choices=["text", "json"], default="text")
    p_prof.add_argument("--fail-on-change", action="store_true")
    p_prof.set_defaults(func=cmd_compare_profiles)

    p_snap = sub.add_parser("snapshots", help="Compare two snapshot files")
    p_snap.add_argument("snapshot_a")
    p_snap.add_argument("snapshot_b")
    p_snap.add_argument("--format", choices=["text", "json"], default="text")
    p_snap.add_argument("--fail-on-change", action="store_true")
    p_snap.set_defaults(func=cmd_compare_snapshots)

    if subparsers is None:
        return parser


def main():
    parser = build_comparator_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
