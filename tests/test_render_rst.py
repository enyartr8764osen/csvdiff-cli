"""Tests for csvdiff.render_rst."""

import pytest
from csvdiff.core import DiffResult
from csvdiff.render_rst import render_rst


def _empty_diff():
    return DiffResult(
        columns=["id", "name", "value"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_changes_produces_no_diff_message():
    result = render_rst(_empty_diff())
    assert result.strip() == "No differences found."


def test_added_row_appears_in_added_section():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "10"})
    result = render_rst(diff)
    assert "Added Rows" in result
    assert "Alice" in result
    assert "Removed Rows" not in result
    assert "Changed Rows" not in result


def test_removed_row_appears_in_removed_section():
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob", "value": "20"})
    result = render_rst(diff)
    assert "Removed Rows" in result
    assert "Bob" in result
    assert "Added Rows" not in result


def test_changed_row_shows_old_and_new():
    diff = _empty_diff()
    diff.changed.append({
        "old": {"id": "3", "name": "Carol", "value": "30"},
        "new": {"id": "3", "name": "Carol", "value": "99"},
    })
    result = render_rst(diff)
    assert "Changed Rows (old)" in result
    assert "Changed Rows (new)" in result
    assert "30" in result
    assert "99" in result


def test_table_contains_rst_grid_borders():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Dave", "value": "5"})
    result = render_rst(diff)
    # RST grid tables use + and - for borders
    assert "+" in result
    assert "-" in result
    assert "|" in result


def test_header_separator_uses_equals():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Eve", "value": "7"})
    result = render_rst(diff)
    # RST uses === under headers to distinguish from row separators
    assert "=" in result


def test_multiple_sections_separated_by_blank_lines():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Frank", "value": "1"})
    diff.removed.append({"id": "2", "name": "Grace", "value": "2"})
    result = render_rst(diff)
    assert "Added Rows" in result
    assert "Removed Rows" in result
    # Sections should be separated by blank lines
    assert "\n\n" in result


def test_column_headers_appear_in_table():
    diff = _empty_diff()
    diff.added.append({"id": "10", "name": "Hank", "value": "42"})
    result = render_rst(diff)
    for col in ["id", "name", "value"]:
        assert col in result
