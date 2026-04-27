"""Tests for csvdiff.render_kdl."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_kdl import _escape, _quote, render_kdl


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_kdl(diff, buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# _escape / _quote helpers
# ---------------------------------------------------------------------------

def test_escape_plain_string_unchanged():
    assert _escape("hello") == "hello"


def test_escape_double_quote():
    assert _escape('say "hi"') == 'say \\"hi\\"'


def test_escape_backslash():
    assert _escape("a\\b") == "a\\\\b"


def test_quote_wraps_in_double_quotes():
    assert _quote("hello") == '"hello"'


# ---------------------------------------------------------------------------
# Structural tests
# ---------------------------------------------------------------------------

def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert _render(diff) == ""


def test_no_changes_produces_three_sections():
    output = _render(_empty_diff())
    assert "added {" in output
    assert "removed {" in output
    assert "changed {" in output


def test_no_changes_sections_are_empty():
    output = _render(_empty_diff())
    # Each section should close immediately without row nodes
    for section in ("added", "removed", "changed"):
        assert f"{section} {{\n}}" in output


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    output = _render(diff)
    assert 'row id="1" name="Alice"' in output
    assert output.index("added") < output.index('row id="1"')


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    output = _render(diff)
    assert 'row id="2" name="Bob"' in output
    assert output.index("removed") < output.index('row id="2"')


def test_changed_row_shows_before_and_after():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(old, new)],
    )
    output = _render(diff)
    assert 'before id="3" name="Carol"' in output
    assert 'after id="3" name="Caroline"' in output


def test_special_characters_are_escaped():
    diff = DiffResult(
        columns=["id", "value"],
        added=[{"id": "1", "value": 'say "hello"'}],
        removed=[],
        changed=[],
    )
    output = _render(diff)
    assert '\\"hello\\"' in output
