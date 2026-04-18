"""CLI subcommands for profile management."""

import argparse
import sys
from pathlib import Path

from envoy_diff.profile import save_profile, load_profile, list_profiles, delete_profile, DEFAULT_PROFILE_DIR
from envoy_diff.parser import parse_env_file
from envoy_diff.profile_diff import diff_profiles, report_profiles, ProfileDiffError
from envoy_diff.formatter import format_text
from envoy_diff.reporter import render_report_text


def cmd_save(args):
    env = parse_env_file(args.env_file)
    path = save_profile(args.name, env, profile_dir=Path(args.profile_dir))
    print(f"Profile '{args.name}' saved to {path}")


def cmd_list(args):
    names = list_profiles(profile_dir=Path(args.profile_dir))
    if not names:
        print("No profiles saved.")
    else:
        for name in names:
            print(f"  {name}")


def cmd_delete(args):
    deleted = delete_profile(args.name, profile_dir=Path(args.profile_dir))
    if deleted:
        print(f"Profile '{args.name}' deleted.")
    else:
        print(f"Profile '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_diff(args):
    try:
        result = diff_profiles(args.profile_a, args.profile_b, profile_dir=Path(args.profile_dir))
    except ProfileDiffError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    print(format_text(result, color=not args.no_color))


def cmd_report(args):
    try:
        report = report_profiles(args.profile_a, args.profile_b, profile_dir=Path(args.profile_dir))
    except ProfileDiffError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    print(render_report_text(report, color=not args.no_color))


def cmd_show(args):
    """Print the contents of a saved profile as key=value lines."""
    try:
        env = load_profile(args.name, profile_dir=Path(args.profile_dir))
    except FileNotFoundError:
        print(f"Profile '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    for key, value in sorted(env.items()):
        print(f"{key}={value}")


def build_profile_parser(subparsers):
    p = subparsers.add_parser("profile", help="Manage env profiles")
    p.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR))
    sub = p.add_subparsers(dest="profile_cmd", required=True)

    ps = sub.add_parser("save", help="Save env file as a named profile")
    ps.add_argument("name")
    ps.add_argument("env_file")
    ps.set_defaults(func=cmd_save)

    pl = sub.add_parser("list", help="List saved profiles")
    pl.set_defaults(func=cmd_list)

    pshow = sub.add_parser("show", help="Show contents of a saved profile")
    pshow.add_argument("name")
    pshow.set_defaults(func=cmd_show)

    pd = sub.add_parser("delete", help="Delete a profile")
    pd.add_argument("name")
    pd.set_defaults(func=cmd_delete)

    pdiff = sub.add_parser("diff", help="Diff two profiles")
    pdiff.add_argument("profile_a")
    pdiff.add_argument("profile_b")
    pdiff.add_argument("--no-color", action="store_true")
    pdiff.set_defaults(func=cmd_diff)

    prep = sub.add_parser("report", help="Audit report for two profiles")
    prep.add_argument("profile_a")
    prep.add_argument("profile_b")
    prep.add_argument("--no-color", action="store_true")
    prep.set_defaults(func=cmd_report)
