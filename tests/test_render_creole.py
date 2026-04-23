"""Tests for csvdiff.render_creole."""
from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_creole import render_creole


def _empty_diff(columns=None):
    cols = columns if columns is not None else ["id", "name", "value"]
    return DiffResult(columns=cols, added=[], removed=[], changed=[])


def test_no_columns_returns_empty_string():
    diff = _empty_diff(columns=[])
    assert render_creole(diff) == ""


def test_no_changes_produces_no_rows_messages():
    result = render_creole(_empty_diff())
    assert "(no rows)" in result


def test_section_headers_present():
    result = render_creole(_empty_diff())
    assert "== Added Rows ==" in result
    assert "== Removed Rows ==" in result


def test_added_row_appears_in_added_section():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "10"})
    result = render_creole(diff)
    assert "== Added Rows ==" in result
    assert "Alice" in result


def test_removed_row_appears_in_removed_section():
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob", "value": "20"})
    result = render_creole(diff)
    assert "== Removed Rows ==" in result
    assert "Bob" in result


def test_changed_row_shows_before_and_after():
    diff = _empty_diff()
    old = {"id": "3", "name": "Carol", "value": "30"}
    new = {"id": "3", "name": "Carol", "value": "99"}
    diff.changed.append((old, new))
    result = render_creole(diff)
    assert "== Changed Rows (before) ==" in result
    assert "== Changed Rows (after) ==" in result
    assert "30" in result
    assert "99" in result


def test_header_uses_bold_markup():
    diff = _empty_diff(columns=["id", "name"])
    diff.added.append({"id": "1", "name": "Dave"})
    result = render_creole(diff)
    assert "**id**" in result
    assert "**name**" in result


def test_rows_use_pipe_delimiter():
    diff = _empty_diff(columns=["id", "name"])
    diff.added.append({"id": "5", "name": "Eve"})
    result = render_creole(diff)
    lines = result.splitlines()
    table_lines = [l for l in lines if l.startswith("|")]
    assert len(table_lines) >= 2  # header + data row
    for line in table_lines:
        assert line.startswith("|") and line.endswith("|")


def test_multiple_sections_separated_by_blank_line():
    diff = _empty_diff(columns=["id", "val"])
    diff.added.append({"id": "1", "val": "a"})
    diff.removed.append({"id": "2", "val": "b"})
    result = render_creole(diff)
    assert "\n\n" in result
