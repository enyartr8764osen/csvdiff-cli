"""Tests for render_dokuwiki."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.render_dokuwiki import render_dokuwiki


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_changes_produces_empty_string():
    assert render_dokuwiki(_empty_diff()) == ""


def test_no_columns_produces_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_dokuwiki(diff) == ""


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_dokuwiki(diff)
    assert "Added Rows" in result
    assert "Alice" in result


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_dokuwiki(diff)
    assert "Removed Rows" in result
    assert "Bob" in result


def test_changed_row_shows_old_and_new():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(columns=["id", "name"], added=[], removed=[], changed=[(old, new)])
    result = render_dokuwiki(diff)
    assert "Before" in result
    assert "After" in result
    assert "Carol" in result
    assert "Caroline" in result


def test_header_row_uses_caret_delimiters():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_dokuwiki(diff)
    header_line = [l for l in result.splitlines() if l.startswith("^")][0]
    assert header_line.startswith("^ ")
    assert header_line.endswith(" ^")


def test_data_row_uses_pipe_delimiters():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_dokuwiki(diff)
    data_line = [l for l in result.splitlines() if l.startswith("|")][0]
    assert data_line.startswith("| ")
    assert data_line.endswith(" |")
