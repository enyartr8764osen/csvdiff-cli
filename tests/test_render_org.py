"""Tests for render_org."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.render_org import render_org


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_changes_produces_empty_string():
    result = render_org(_empty_diff())
    assert result.strip() == ""


def test_no_columns_produces_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_org(diff) == ""


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_org(diff)
    assert "* Added" in result
    assert "Alice" in result


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_org(diff)
    assert "* Removed" in result
    assert "Bob" in result


def test_changed_row_shows_before_and_after():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[{"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}],
    )
    result = render_org(diff)
    assert "* Changed" in result
    assert "Carol" in result
    assert "Caroline" in result


def test_table_uses_pipe_syntax():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_org(diff)
    lines = [l for l in result.splitlines() if l.startswith("|")]
    assert len(lines) >= 2
    for line in lines:
        assert line.startswith("|")
        assert line.endswith("|")


def test_header_separator_uses_plus():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_org(diff)
    sep_lines = [l for l in result.splitlines() if "+" in l and l.startswith("|")]
    assert len(sep_lines) >= 1
