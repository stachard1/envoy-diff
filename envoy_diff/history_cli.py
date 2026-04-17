"""CLI commands for snapshot history management."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envoy_diff.history import (
    record_snapshot,
    list_history,
    load_history_entry,
    get_latest,
    purge_history,
)
from envoy_diff.parser import parse_env_file
from envoy_diff.differ import diff_envs
from envoy_diff.formatter import format_text

DEFAULT_HISTORY_DIR = ".envoy_history"


def cmd_record(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    path = record_snapshot(env, args.label, args.history_dir)
    print(f"Snapshot recorded: {path}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    history = list_history(args.history_dir)
    if not history:
        print("No history entries found.")
        return 0
    for entry in history:
        print(f"[{entry['timestamp']}] {entry['label']}  -> {entry['path']}")
    return 0


def cmd_diff_latest(args: argparse.Namespace) -> int:
    entry = get_latest(args.label, args.history_dir)
    if entry is None:
        print(f"No history found for label: {args.label}", file=sys.stderr)
        return 2
    try:
        current = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    baseline = load_history_entry(entry)
    result = diff_envs(baseline, current)
    print(format_text(result, color=False))
    return 0


def cmd_purge(args: argparse.Namespace) -> int:
    removed = purge_history(args.history_dir)
    print(f"Purged {removed} history entries.")
    return 0


def build_history_parser(subparsers=None):
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="envoy-history")
        sub = parser.add_subparsers(dest="command")
    else:
        parser = subparsers.add_parser("history", help="Manage snapshot history")
        sub = parser.add_subparsers(dest="history_command")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--history-dir", default=DEFAULT_HISTORY_DIR)

    rec = sub.add_parser("record", parents=[common])
    rec.add_argument("label")
    rec.add_argument("env_file")
    rec.set_defaults(func=cmd_record)

    ls = sub.add_parser("list", parents=[common])
    ls.set_defaults(func=cmd_list)

    dff = sub.add_parser("diff", parents=[common])
    dff.add_argument("label")
    dff.add_argument("env_file")
    dff.set_defaults(func=cmd_diff_latest)

    purge = sub.add_parser("purge", parents=[common])
    purge.set_defaults(func=cmd_purge)

    return parser


def main(argv: List[str] = None) -> int:
    parser = build_history_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)
