"""Integration tests for render_dot with realistic multi-row diffs."""
from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_dot import render_dot


def _make_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "city", "pop"],
        added=[
            {"id": "10", "city": "Alpha", "pop": "1000"},
            {"id": "11", "city": "Beta", "pop": "2000"},
        ],
        removed=[
            {"id": "20", "city": "Gamma", "pop": "3000"},
        ],
        changed=[
            (
                {"id": "30", "city": "Delta", "pop": "400"},
                {"id": "30", "city": "Delta", "pop": "500"},
            )
        ],
    )


def test_all_added_rows_appear():
    result = render_dot(_make_diff())
    assert "Alpha" in result
    assert "Beta" in result


def test_removed_row_appears():
    result = render_dot(_make_diff())
    assert "Gamma" in result


def test_changed_rows_both_appear():
    result = render_dot(_make_diff())
    assert result.count("Delta") == 2


def test_output_is_valid_dot_structure():
    result = render_dot(_make_diff())
    lines = result.strip().splitlines()
    assert lines[0].startswith("graph ")
    assert lines[0].endswith("{")
    assert lines[-1] == "}"


def test_node_ids_are_unique():
    result = render_dot(_make_diff())
    node_lines = [ln.strip() for ln in result.splitlines() if "[shape=" in ln]
    node_ids = [ln.split(" ")[0] for ln in node_lines]
    assert len(node_ids) == len(set(node_ids))
