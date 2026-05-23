"""Tests for csvdiff.render_dot."""
from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_dot import render_dot


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_dot(diff) == ""


def test_empty_diff_opens_and_closes_graph():
    result = render_dot(_empty_diff())
    assert result.strip().startswith("graph ")
    assert result.strip().endswith("}")


def test_default_graph_name_appears_in_output():
    result = render_dot(_empty_diff())
    assert "csvdiff" in result


def test_custom_graph_name_appears_in_output():
    result = render_dot(_empty_diff(), graph_name="mydiff")
    assert "mydiff" in result


def test_no_preamble_omits_graph_declaration():
    result = render_dot(_empty_diff(), include_preamble=False)
    assert not result.strip().startswith("graph ")


def test_added_row_produces_lightgreen_node():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_dot(diff)
    assert "lightgreen" in result
    assert "Alice" in result


def test_removed_row_produces_lightcoral_node():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_dot(diff)
    assert "lightcoral" in result
    assert "Bob" in result


def test_changed_row_produces_two_nodes_and_edge():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(columns=["id", "name"], added=[], removed=[], changed=[(old, new)])
    result = render_dot(diff)
    assert "lightyellow" in result
    assert "lightblue" in result
    assert "changed" in result
    assert "Carol" in result
    assert "Caroline" in result


def test_escape_double_quote_in_value():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": 'say "hi"'}],
        removed=[],
        changed=[],
    )
    result = render_dot(diff)
    assert '\\"' in result


def test_multiple_added_rows_all_appear():
    diff = DiffResult(
        columns=["id"],
        added=[{"id": "1"}, {"id": "2"}, {"id": "3"}],
        removed=[],
        changed=[],
    )
    result = render_dot(diff)
    assert result.count("lightgreen") == 3
