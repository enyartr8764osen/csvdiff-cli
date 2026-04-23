"""Tests for csvdiff.render_rtf."""

from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_rtf import _escape, render_rtf


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


# ---------------------------------------------------------------------------
# _escape helpers
# ---------------------------------------------------------------------------

def test_escape_backslash():
    assert _escape("\\") == "\\\\"


def test_escape_open_brace():
    assert _escape("{") == "\\{"


def test_escape_close_brace():
    assert _escape("}") == "\\}"


def test_escape_plain_text_unchanged():
    assert _escape("hello world") == "hello world"


# ---------------------------------------------------------------------------
# render_rtf structural tests
# ---------------------------------------------------------------------------

def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_rtf(diff) == ""


def test_output_starts_with_rtf_header():
    result = render_rtf(_empty_diff())
    assert result.startswith("{\\rtf1")


def test_output_ends_with_closing_brace():
    result = render_rtf(_empty_diff())
    assert result.strip().endswith("}")


def test_no_changes_produces_no_differences_message():
    result = render_rtf(_empty_diff())
    assert "No differences found" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_rtf(diff)
    assert "Added Rows" in result
    assert "Alice" in result


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_rtf(diff)
    assert "Removed Rows" in result
    assert "Bob" in result


def test_changed_row_shows_before_and_after():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(old, new)],
    )
    result = render_rtf(diff)
    assert "Changed Rows" in result
    assert "Carol" in result
    assert "Caroline" in result
    assert "Before" in result
    assert "After" in result


def test_special_characters_are_escaped():
    diff = DiffResult(
        columns=["id", "value"],
        added=[{"id": "1", "value": "a{b}c"}],
        removed=[],
        changed=[],
    )
    result = render_rtf(diff)
    assert "a\\{b\\}c" in result
