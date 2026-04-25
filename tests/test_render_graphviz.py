"""Tests for csvdiff.render_graphviz."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_graphviz import render_graphviz


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult, **kwargs) -> str:
    buf = io.StringIO()
    render_graphviz(diff, buf, **kwargs)
    return buf.getvalue()


def test_no_columns_returns_minimal_graph():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    out = _render(diff)
    assert "digraph csvdiff" in out
    assert out.strip().endswith("}")


def test_empty_diff_opens_and_closes_digraph():
    out = _render(_empty_diff())
    assert out.startswith("digraph csvdiff {")
    assert out.strip().endswith("}")


def test_custom_graph_name_appears_in_output():
    out = _render(_empty_diff(), graph_name="my_graph")
    assert "digraph my_graph {" in out


def test_added_row_appears_in_added_subgraph():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert "cluster_added" in out
    assert "Added" in out
    assert "Alice" in out


def test_removed_row_appears_in_removed_subgraph():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    out = _render(diff)
    assert "cluster_removed" in out
    assert "Removed" in out
    assert "Bob" in out


def test_changed_row_shows_old_and_new_nodes_with_edge():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(
            {"id": "3", "name": "Carol"},
            {"id": "3", "name": "Caroline"},
        )],
    )
    out = _render(diff)
    assert "cluster_changed" in out
    assert "Carol" in out
    assert "Caroline" in out
    assert "->" in out
    assert "updated" in out


def test_no_added_section_when_no_added_rows():
    out = _render(_empty_diff())
    assert "cluster_added" not in out


def test_special_characters_are_escaped():
    diff = DiffResult(
        columns=["id", "note"],
        added=[{"id": "1", "note": 'say "hello"'}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert '\\"hello\\"' in out
