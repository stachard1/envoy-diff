"""Dependency graph builder for environment variable relationships."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envoy_diff.differ import EnvDiffResult, diff_envs
from envoy_diff.tagger import tag_key


@dataclass
class GraphNode:
    key: str
    tags: List[str]
    dependents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class EnvGraph:
    nodes: Dict[str, GraphNode]
    changed_keys: Set[str]

    def impacted_keys(self) -> List[str]:
        """Return all keys impacted by changes, including dependents."""
        impacted: Set[str] = set(self.changed_keys)
        for key in list(self.changed_keys):
            node = self.nodes.get(key)
            if node:
                impacted.update(node.dependents)
        return sorted(impacted)

    def summary(self) -> str:
        changed = len(self.changed_keys)
        impacted = len(self.impacted_keys())
        return f"{changed} key(s) changed, {impacted} total impacted (including dependents)"


def _infer_dependencies(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Infer dependencies by scanning values for references to other keys."""
    deps: Dict[str, List[str]] = {k: [] for k in env}
    keys = set(env.keys())
    for key, value in env.items():
        for other_key in keys:
            if other_key != key and other_key in value:
                deps[key].append(other_key)
    return deps


def build_graph(before: Dict[str, str], after: Dict[str, str]) -> EnvGraph:
    """Build a dependency graph from two environment snapshots."""
    combined = {**before, **after}
    deps = _infer_dependencies(combined)

    # Build reverse map: dependents[k] = list of keys whose value references k
    dependents: Dict[str, List[str]] = {k: [] for k in combined}
    for key, dep_list in deps.items():
        for dep in dep_list:
            if dep in dependents:
                dependents[dep].append(key)

    nodes: Dict[str, GraphNode] = {}
    for key in combined:
        nodes[key] = GraphNode(
            key=key,
            tags=tag_key(key),
            dependents=dependents.get(key, []),
            dependencies=deps.get(key, []),
        )

    diff: EnvDiffResult = diff_envs(before, after)
    changed: Set[str] = (
        set(diff.added) | set(diff.removed) | set(diff.changed)
    )

    return EnvGraph(nodes=nodes, changed_keys=changed)
