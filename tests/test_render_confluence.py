"""Tests for render_confluence."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.render_confluence import render_confluence


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_confluence(diff) == ""


def test_no_changes_produces_no_rows_messages():
    result = render_confluence(_empty_diff())
    assert "No rows." in result


def test_section_headers_present():
    result = render_confluence(_empty_diff())
    assert "h3. Added Rows" in result
    assert "h3. Removed Rows" in result
    assert "h3. Changed Rows (Before)" in result
    assert "h3. Changed Rows (After)" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_confluence(diff)
    assert "Alice" in result
    lines = result.splitlines()
    added_idx = next(i for i, l in enumerate(lines) if "Added Rows" in l)
    data_lines = [l for l in lines[added_idx:] if l.startswith("|") and not l.startswith("||")]
    assert any("Alice" in l for l in data_lines)


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_confluence(diff)
    assert "Bob" in result


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[{"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}],
    )
    result = render_confluence(diff)
    assert "Carol" in result
    assert "Caroline" in result


def test_header_uses_double_pipe():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_confluence(diff)
    assert "||" in result
