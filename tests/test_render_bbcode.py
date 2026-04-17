"""Tests for BBCode renderer."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.render_bbcode import render_bbcode


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_changes_produces_empty_string():
    assert render_bbcode(_empty_diff()) == ""


def test_no_columns_produces_empty_string():
    diff = DiffResult(columns=[], added=[{"id": "1"}], removed=[], changed=[])
    assert render_bbcode(diff) == ""


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_bbcode(diff)
    assert "Added Rows" in result
    assert "Alice" in result
    assert "[table]" in result
    assert "[/table]" in result


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_bbcode(diff)
    assert "Removed Rows" in result
    assert "Bob" in result


def test_changed_row_shows_old_and_new_with_colors():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(columns=["id", "name"], added=[], removed=[], changed=[(old, new)])
    result = render_bbcode(diff)
    assert "Changed Rows" in result
    assert "[color=red]" in result
    assert "[color=green]" in result
    assert "Carol" in result
    assert "Caroline" in result


def test_header_row_uses_th_tags():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_bbcode(diff)
    assert "[th]" in result
    assert "[/th]" in result


def test_data_row_uses_td_tags():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_bbcode(diff)
    assert "[td]" in result
    assert "[/td]" in result
