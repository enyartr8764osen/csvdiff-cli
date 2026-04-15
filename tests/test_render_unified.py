"""Tests for csvdiff.render_unified."""
from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_unified import render_unified


def _empty_diff(columns=None):
    return DiffResult(
        columns=columns or ["id", "name", "value"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_changes_produces_no_output():
    diff = _empty_diff()
    assert render_unified(diff) == ""


def test_no_columns_produces_no_output():
    diff = _empty_diff(columns=[])
    assert render_unified(diff) == ""


def test_added_row_has_plus_prefix():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "10"})
    output = render_unified(diff)
    assert "+1,Alice,10" in output


def test_removed_row_has_minus_prefix():
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob", "value": "20"})
    output = render_unified(diff)
    assert "-2,Bob,20" in output


def test_changed_row_shows_old_minus_and_new_plus():
    diff = _empty_diff()
    old = {"id": "3", "name": "Carol", "value": "30"}
    new = {"id": "3", "name": "Carol", "value": "99"}
    diff.changed.append((old, new))
    output = render_unified(diff)
    assert "-3,Carol,30" in output
    assert "+3,Carol,99" in output


def test_header_line_lists_columns():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "10"})
    output = render_unified(diff)
    assert "@@ columns: id,name,value @@" in output


def test_output_starts_with_diff_markers():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "X", "value": "0"})
    lines = render_unified(diff).splitlines()
    assert lines[0] == "--- a"
    assert lines[1] == "+++ b"


def test_output_ends_with_newline():
    diff = _empty_diff()
    diff.removed.append({"id": "5", "name": "Eve", "value": "50"})
    assert render_unified(diff).endswith("\n")


def test_missing_column_value_rendered_as_empty_string():
    diff = _empty_diff()
    diff.added.append({"id": "7", "name": "Zara"})  # 'value' key absent
    output = render_unified(diff)
    assert "+7,Zara," in output
