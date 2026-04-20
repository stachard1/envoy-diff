"""CLI sub-command: patch — apply env diff as a patch to a base file."""

import argparse
import json
import sys
from typing import List, Optional

from envoy_diff.parser import parse_env_file
from envoy_diff.patcher import patch_envs


def build_patch_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    desc = "Apply changes from <target> onto <base> env file."
    if sub is not None:
        p = sub.add_parser("patch", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="envoy-patch", description=desc)

    p.add_argument("base", help="Base .env file")
    p.add_argument("target", help="Target .env file whose changes are applied")
    p.add_argument(
        "--skip",
        metavar="KEY",
        nargs="+",
        default=[],
        help="Keys to leave unchanged from base",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--out",
        metavar="FILE",
        help="Write patched env to FILE instead of stdout",
    )
    return p


def cmd_patch(args: argparse.Namespace) -> int:
    try:
        base_env = parse_env_file(args.base)
        target_env = parse_env_file(args.target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = patch_envs(base_env, target_env, skip_keys=args.skip)

    if args.format == "json":
        output = json.dumps(
            {
                "patched": result.patched,
                "applied": result.applied,
                "skipped": result.skipped,
            },
            indent=2,
        )
    else:
        lines = [f"{k}={v}" for k, v in sorted(result.patched.items())]
        output = "\n".join(lines)
        if result.skipped:
            print(f"# skipped: {', '.join(sorted(result.skipped))}", file=sys.stderr)

    if args.out:
        with open(args.out, "w") as fh:
            fh.write(output + "\n")
    else:
        print(output)

    return 0


def main(argv=None) -> None:
    parser = build_patch_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_patch(args))


if __name__ == "__main__":
    main()
