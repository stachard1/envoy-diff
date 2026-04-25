"""CLI entry point for the environment dependency graph feature."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.differ_graph import build_graph
from envoy_diff.parser import parse_env_file


def build_graph_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser("graph", help="Show dependency graph for env changes")
    p.add_argument("before", help="Path to the 'before' env file")
    p.add_argument("after", help="Path to the 'after' env file")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--impacted-only",
        action="store_true",
        help="Only show keys impacted by changes",
    )
    return p


def cmd_graph(args: argparse.Namespace) -> int:
    try:
        before = parse_env_file(args.before)
        after = parse_env_file(args.after)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    graph = build_graph(before, after)

    if args.format == "json":
        keys_to_show = (
            graph.impacted_keys() if args.impacted_only else sorted(graph.nodes)
        )
        output = {
            "summary": graph.summary(),
            "changed": sorted(graph.changed_keys),
            "impacted": graph.impacted_keys(),
            "nodes": {
                k: {
                    "tags": graph.nodes[k].tags,
                    "dependencies": graph.nodes[k].dependencies,
                    "dependents": graph.nodes[k].dependents,
                }
                for k in keys_to_show
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(graph.summary())
        keys_to_show = (
            graph.impacted_keys() if args.impacted_only else sorted(graph.nodes)
        )
        for key in keys_to_show:
            node = graph.nodes[key]
            marker = "*" if key in graph.changed_keys else " "
            tags = f"[{', '.join(node.tags)}]" if node.tags else ""
            deps = f"  deps: {node.dependencies}" if node.dependencies else ""
            print(f"  {marker} {key} {tags}{deps}")

    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="envoy-graph")
    sub = parser.add_subparsers(dest="command")
    build_graph_parser(sub)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 1
    return cmd_graph(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
