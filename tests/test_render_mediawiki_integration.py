"""Integration-style tests for render_mediawiki covering column alignment."""

from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_mediawiki import render_mediawiki


def _make_diff(
    columns=None,
    added=None,
    removed=None,
    changed=None,
) -> DiffResult:
    return DiffResult(
        columns=columns or ["id", "value"],
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def test_multiple_added_rows_all_appear():
    diff = _make_diff(
        added=[
            {"id": "1", "value": "alpha"},
            {"id": "2", "value": "beta"},
            {"id": "3", "value": "gamma"},
        ]
    )
    result = render_mediawiki(diff)
    assert "alpha" in result
    assert "beta" in result
    assert "gamma" in result


def test_table_rows_start_with_pipe():
    diff = _make_diff(added=[{"id": "1", "value": "x"}])
    result = render_mediawiki(diff)
    data_lines = [l for l in result.splitlines() if l.startswith("| ") and "wikitable" not in l]
    assert data_lines, "Expected data rows starting with '| '"


def test_row_separator_present():
    diff = _make_diff(added=[{"id": "1", "value": "x"}])
    result = render_mediawiki(diff)
    assert "|-" in result


def test_table_closed_with_pipe_brace():
    diff = _make_diff(added=[{"id": "1", "value": "x"}])
    result = render_mediawiki(diff)
    assert "|}" in result


def test_only_changed_rows_shows_both_before_and_after():
    diff = _make_diff(
        changed=[
            {"old": {"id": "10", "value": "old_val"}, "new": {"id": "10", "value": "new_val"}}
        ]
    )
    result = render_mediawiki(diff)
    assert "old_val" in result
    assert "new_val" in result
    assert "== Added Rows ==" not in result
    assert "== Removed Rows ==" not in result
