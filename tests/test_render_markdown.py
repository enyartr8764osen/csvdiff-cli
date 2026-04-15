"""Tests for the Markdown renderer."""

import pytest
from csvdiff.core import DiffResult
from csvdiff.render_markdown import render_markdown


def _empty_diff():
    return DiffResult(added=[], removed=[], changed={})


def test_no_changes_produces_no_diff_message():
    output = render_markdown(_empty_diff())
    assert "No differences found" in output
    assert "##" not in output


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed={},
    )
    output = render_markdown(diff)
    assert "## Added Rows" in output
    assert "Alice" in output
    assert "added" in output
    assert "## Removed Rows" not in output
    assert "## Changed Rows" not in output


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed={},
    )
    output = render_markdown(diff)
    assert "## Removed Rows" in output
    assert "Bob" in output
    assert "removed" in output
    assert "## Added Rows" not in output


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        added=[],
        removed=[],
        changed={
            ("3",): {
                "old": {"id": "3", "name": "Carol"},
                "new": {"id": "3", "name": "Caroline"},
            }
        },
    )
    output = render_markdown(diff)
    assert "## Changed Rows" in output
    assert "Carol" in output
    assert "Caroline" in output
    assert "old" in output
    assert "new" in output


def test_table_contains_separator_row():
    diff = DiffResult(
        added=[{"id": "1", "val": "x"}],
        removed=[],
        changed={},
    )
    output = render_markdown(diff)
    # Markdown separator lines contain dashes between pipes
    assert "|---" in output or "| -" in output


def test_multiple_sections_rendered_together():
    diff = DiffResult(
        added=[{"id": "10", "city": "Paris"}],
        removed=[{"id": "20", "city": "Rome"}],
        changed={},
    )
    output = render_markdown(diff)
    assert "## Added Rows" in output
    assert "## Removed Rows" in output
    assert "Paris" in output
    assert "Rome" in output
