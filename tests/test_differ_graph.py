"""Tests for envoy_diff.differ_graph and graph_cli."""
from __future__ import annotations

import json
import os
import textwrap
from argparse import Namespace

import pytest

from envoy_diff.differ_graph import build_graph, EnvGraph, GraphNode
from envoy_diff.graph_cli import cmd_graph


@pytest.fixture()
def before() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_URL": "postgres://localhost:5432/mydb",
        "APP_SECRET": "old-secret",
        "PORT": "8080",
    }


@pytest.fixture()
def after() -> dict:
    return {
        "DB_HOST": "prod-db",
        "DB_URL": "postgres://prod-db:5432/mydb",
        "APP_SECRET": "new-secret",
        "PORT": "8080",
    }


def test_build_graph_returns_env_graph(before, after):
    graph = build_graph(before, after)
    assert isinstance(graph, EnvGraph)


def test_changed_keys_detected(before, after):
    graph = build_graph(before, after)
    assert "DB_HOST" in graph.changed_keys
    assert "APP_SECRET" in graph.changed_keys


def test_unchanged_keys_not_in_changed(before, after):
    graph = build_graph(before, after)
    assert "PORT" not in graph.changed_keys


def test_dependency_inferred_from_value(before, after):
    # DB_URL contains DB_HOST in its value
    graph = build_graph(before, after)
    node = graph.nodes["DB_URL"]
    assert "DB_HOST" in node.dependencies


def test_dependents_reverse_of_dependencies(before, after):
    graph = build_graph(before, after)
    db_host_node = graph.nodes["DB_HOST"]
    assert "DB_URL" in db_host_node.dependents


def test_impacted_keys_includes_dependents(before, after):
    graph = build_graph(before, after)
    impacted = graph.impacted_keys()
    # DB_HOST changed -> DB_URL should be impacted
    assert "DB_HOST" in impacted
    assert "DB_URL" in impacted


def test_unchanged_non_dependent_not_impacted(before, after):
    graph = build_graph(before, after)
    impacted = graph.impacted_keys()
    assert "PORT" not in impacted


def test_summary_contains_counts(before, after):
    graph = build_graph(before, after)
    s = graph.summary()
    assert "changed" in s
    assert "impacted" in s


def test_nodes_have_tags(before, after):
    graph = build_graph(before, after)
    node = graph.nodes["APP_SECRET"]
    assert isinstance(node.tags, list)
    assert len(node.tags) > 0  # APP_SECRET should be tagged as sensitive


def test_cmd_graph_text_output(before, after, tmp_path, capsys):
    b = tmp_path / "before.env"
    a = tmp_path / "after.env"
    b.write_text("\n".join(f"{k}={v}" for k, v in before.items()))
    a.write_text("\n".join(f"{k}={v}" for k, v in after.items()))
    args = Namespace(before=str(b), after=str(a), format="text", impacted_only=False)
    rc = cmd_graph(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "changed" in out
    assert "DB_HOST" in out


def test_cmd_graph_json_output(before, after, tmp_path, capsys):
    b = tmp_path / "before.env"
    a = tmp_path / "after.env"
    b.write_text("\n".join(f"{k}={v}" for k, v in before.items()))
    a.write_text("\n".join(f"{k}={v}" for k, v in after.items()))
    args = Namespace(before=str(b), after=str(a), format="json", impacted_only=False)
    rc = cmd_graph(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "nodes" in data
    assert "changed" in data
    assert "impacted" in data


def test_cmd_graph_missing_file_returns_2(tmp_path, capsys):
    args = Namespace(
        before=str(tmp_path / "missing.env"),
        after=str(tmp_path / "also_missing.env"),
        format="text",
        impacted_only=False,
    )
    rc = cmd_graph(args)
    assert rc == 2
