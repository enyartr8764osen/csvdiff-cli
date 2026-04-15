"""Tests for csvdiff.render_latex."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_latex import render_latex, _escape


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_latex(diff, buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# _escape
# ---------------------------------------------------------------------------

def test_escape_ampersand():
    assert _escape("a & b") == r"a \& b"


def test_escape_underscore():
    assert _escape("col_name") == r"col\_name"


def test_escape_percent():
    assert _escape("50%") == r"50\%"


# ---------------------------------------------------------------------------
# no changes
# ---------------------------------------------------------------------------

def test_no_changes_produces_comment():
    out = _render(_empty_diff())
    assert "% No differences found." in out


def test_no_changes_has_no_longtable():
    out = _render(_empty_diff())
    assert "longtable" not in out


# ---------------------------------------------------------------------------
# added rows
# ---------------------------------------------------------------------------

def test_added_row_appears_in_added_section():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    out = _render(diff)
    assert "Added Rows" in out
    assert "Alice" in out


def test_added_row_uses_green_color():
    diff = _empty_diff()
    diff.added.append({"id": "2", "name": "Bob"})
    out = _render(diff)
    assert "green" in out


# ---------------------------------------------------------------------------
# removed rows
# ---------------------------------------------------------------------------

def test_removed_row_appears_in_removed_section():
    diff = _empty_diff()
    diff.removed.append({"id": "3", "name": "Carol"})
    out = _render(diff)
    assert "Removed Rows" in out
    assert "Carol" in out


def test_removed_row_uses_red_color():
    diff = _empty_diff()
    diff.removed.append({"id": "4", "name": "Dave"})
    out = _render(diff)
    assert "red" in out


# ---------------------------------------------------------------------------
# changed rows
# ---------------------------------------------------------------------------

def test_changed_row_shows_old_and_new():
    diff = _empty_diff()
    old = {"id": "5", "name": "Eve"}
    new = {"id": "5", "name": "Evelyn"}
    diff.changed.append((old, new))
    out = _render(diff)
    assert "Changed Rows" in out
    assert "Eve" in out
    assert "Evelyn" in out


def test_changed_row_uses_blue_for_new():
    diff = _empty_diff()
    diff.changed.append(({"id": "6", "name": "Old"}, {"id": "6", "name": "New"}))
    out = _render(diff)
    assert "blue" in out


def test_special_chars_are_escaped():
    diff = _empty_diff()
    diff.added.append({"id": "7", "name": "50% off & more"})
    out = _render(diff)
    assert r"50\%" in out
    assert r"\&" in out
