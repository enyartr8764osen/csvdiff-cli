"""Tests for csvdiff.render_groff."""
from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_groff import render_groff


def _empty_diff(columns=None):
    return DiffResult(
        columns=columns or ["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def test_no_columns_returns_empty_string():
    diff = _empty_diff(columns=[])
    assert render_groff(diff) == ""


def test_preamble_included_by_default():
    result = render_groff(_empty_diff())
    assert ".TH" in result


def test_preamble_omitted_when_flag_false():
    result = render_groff(_empty_diff(), preamble=False)
    assert ".TH" not in result


def test_section_headers_present():
    result = render_groff(_empty_diff())
    assert ".SH Added Rows" in result
    assert ".SH Removed Rows" in result
    assert ".SH Changed Rows (Before)" in result
    assert ".SH Changed Rows (After)" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_groff(diff)
    assert "Alice" in result
    # Should appear before the Removed section
    added_pos = result.index(".SH Added Rows")
    removed_pos = result.index(".SH Removed Rows")
    alice_pos = result.index("Alice")
    assert added_pos < alice_pos < removed_pos


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_groff(diff)
    assert "Bob" in result


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[
            {"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}
        ],
    )
    result = render_groff(diff)
    assert "Carol" in result
    assert "Caroline" in result


def test_tbl_blocks_present_when_rows_exist():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Dave"}],
        removed=[],
        changed=[],
    )
    result = render_groff(diff)
    assert ".TS" in result
    assert ".TE" in result


def test_hyphen_escaped():
    diff = DiffResult(
        columns=["id", "val"],
        added=[{"id": "1", "val": "foo-bar"}],
        removed=[],
        changed=[],
    )
    result = render_groff(diff)
    assert "\\-" in result
