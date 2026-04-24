"""Tests for csvdiff.render_adoc."""
from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_adoc import render_adoc


def _empty_diff(columns=None):
    cols = columns or ["id", "name"]
    return DiffResult(columns=cols, added=[], removed=[], changed=[])


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_adoc(diff) == ""


def test_default_title_in_output():
    result = render_adoc(_empty_diff())
    assert "= CSV Diff Report" in result


def test_custom_title_in_output():
    result = render_adoc(_empty_diff(), title="My Report")
    assert "= My Report" in result


def test_section_headers_present():
    result = render_adoc(_empty_diff())
    assert "== Added Rows" in result
    assert "== Removed Rows" in result
    assert "== Changed Rows" in result


def test_no_changes_shows_no_rows_message():
    result = render_adoc(_empty_diff())
    assert result.count("_No rows._") == 3


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_adoc(diff)
    assert "Alice" in result
    lines = result.splitlines()
    added_idx = next(i for i, l in enumerate(lines) if "== Added Rows" in l)
    removed_idx = next(i for i, l in enumerate(lines) if "== Removed Rows" in l)
    section = "\n".join(lines[added_idx:removed_idx])
    assert "Alice" in section


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_adoc(diff)
    lines = result.splitlines()
    removed_idx = next(i for i, l in enumerate(lines) if "== Removed Rows" in l)
    changed_idx = next(i for i, l in enumerate(lines) if "== Changed Rows" in l)
    section = "\n".join(lines[removed_idx:changed_idx])
    assert "Bob" in section


def test_changed_row_shows_before_and_after():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(columns=["id", "name"], added=[], removed=[], changed=[(old, new)])
    result = render_adoc(diff)
    assert "Carol" in result
    assert "Caroline" in result
    assert ".Before" in result
    assert ".After" in result


def test_table_uses_asciidoc_table_delimiters():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Dave"}],
        removed=[],
        changed=[],
    )
    result = render_adoc(diff)
    assert "|===" in result
