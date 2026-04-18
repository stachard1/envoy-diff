"""CLI integration for risk scoring of env diffs."""
import argparse
import json
import sys
from envoy_diff.parser import parse_env_file
from envoy_diff.differ import diff_envs
from envoy_diff.scorer import score_diff


def build_score_parser(subparsers=None):
    desc = "Score the risk level of environment variable changes"
    if subparsers:
        p = subparsers.add_parser("score", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envoy-score", description=desc)
    p.add_argument("before", help="Path to the before .env file")
    p.add_argument("after", help="Path to the after .env file")
    p.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")
    p.add_argument(
        "--fail-on",
        choices=["low", "medium", "high"],
        default=None,
        help="Exit with code 1 if risk level meets or exceeds this threshold",
    )
    return p


_LEVEL_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}


def run_score(args, out=sys.stdout):
    try:
        before = parse_env_file(args.before)
        after = parse_env_file(args.after)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    diff = diff_envs(before, after)
    score = score_diff(diff)

    if args.as_json:
        data = {"total": score.total, "level": score.level, "breakdown": score.breakdown}
        print(json.dumps(data, indent=2), file=out)
    else:
        print(f"Risk level : {score.level.upper()}", file=out)
        print(f"Risk score : {score.total}", file=out)
        if score.breakdown:
            print("Breakdown  :", file=out)
            for k, v in score.breakdown.items():
                print(f"  {k}: {v}", file=out)

    if args.fail_on and _LEVEL_ORDER[score.level] >= _LEVEL_ORDER[args.fail_on]:
        return 1
    return 0


def main():
    parser = build_score_parser()
    args = parser.parse_args()
    sys.exit(run_score(args))


if __name__ == "__main__":
    main()
