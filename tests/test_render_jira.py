"""Tests for render_jira."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.render_jira import render_jira


def _empty_diff(columns=None):
    return DiffResult(
        columns=columns or ["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_columns_returns_empty_string():
    diff = _empty_diff(columns=[])
    assert render_jira(diff) == ""


def test_no_changes_produces_no_differences_message():
    result = render_jira(_empty_diff())
    assert "No differences found." in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_jira(diff)
    assert "Added Rows" in result
    assert "Alice" in result


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_jira(diff)
    assert "Removed Rows" in result
    assert "Bob" in result


def test_changed_row_shows_before_and_after():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[{"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}],
    )
    result = render_jira(diff)
    assert "Changed Rows" in result
    assert "Before" in result
    assert "After" in result
    assert "Carol" in result
    assert "Caroline" in result


def test_header_uses_double_pipes():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_jira(diff)
    assert "||" in result


def test_data_rows_use_single_pipes():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    lines = render_jira(diff).splitlines()
    data_lines = [l for l in lines if l.startswith("| ") and "||" not in l]
    assert len(data_lines) > 0
