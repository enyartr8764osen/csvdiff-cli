"""Tests for render_asciidoc."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.render_asciidoc import render_asciidoc


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_asciidoc(diff) == ""


def test_no_changes_produces_no_rows_message():
    result = render_asciidoc(_empty_diff())
    assert "_No rows._" in result


def test_section_headers_present():
    result = render_asciidoc(_empty_diff())
    assert "=== Added Rows" in result
    assert "=== Removed Rows" in result
    assert "=== Changed Rows (Before)" in result
    assert "=== Changed Rows (After)" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_asciidoc(diff)
    assert "Alice" in result
    lines = result.splitlines()
    added_idx = next(i for i, l in enumerate(lines) if "Added Rows" in l)
    removed_idx = next(i for i, l in enumerate(lines) if "Removed Rows" in l)
    added_section = "\n".join(lines[added_idx:removed_idx])
    assert "Alice" in added_section


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_asciidoc(diff)
    lines = result.splitlines()
    removed_idx = next(i for i, l in enumerate(lines) if "Removed Rows" in l)
    changed_idx = next(i for i, l in enumerate(lines) if "Changed Rows (Before)" in l)
    removed_section = "\n".join(lines[removed_idx:changed_idx])
    assert "Bob" in removed_section


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[{"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}],
    )
    result = render_asciidoc(diff)
    assert "Carol" in result
    assert "Caroline" in result


def test_table_uses_asciidoc_delimiter():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_asciidoc(diff)
    assert "|===" in result


def test_column_headers_in_output():
    diff = _empty_diff()
    result = render_asciidoc(diff)
    assert "id" in result
    assert "name" in result
