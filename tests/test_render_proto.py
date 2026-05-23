"""Tests for csvdiff.render_proto."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_proto import _escape, render_proto


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_proto(diff, buf)
    return buf.getvalue()


# --- _escape ---

def test_escape_plain_string_unchanged():
    assert _escape("hello") == "hello"


def test_escape_double_quote():
    assert _escape('say "hi"') == 'say \\"hi\\"'


def test_escape_backslash():
    assert _escape("a\\b") == "a\\\\b"


def test_escape_newline():
    assert _escape("line1\nline2") == "line1\\nline2"


# --- render_proto ---

def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert _render(diff) == ""


def test_no_changes_produces_no_output():
    assert _render(_empty_diff()) == ""


def test_added_row_produces_added_block():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert out.startswith("added {")
    assert 'key: "id"' in out
    assert 'value: "1"' in out
    assert 'key: "name"' in out
    assert 'value: "Alice"' in out


def test_removed_row_produces_removed_block():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    out = _render(diff)
    assert "removed {" in out
    assert 'value: "Bob"' in out


def test_changed_row_produces_changed_block_with_before_and_after():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(
            {"id": "3", "name": "Old"},
            {"id": "3", "name": "New"},
        )],
    )
    out = _render(diff)
    assert "changed {" in out
    assert "before {" in out
    assert "after {" in out
    assert 'value: "Old"' in out
    assert 'value: "New"' in out


def test_multiple_added_rows_all_appear():
    diff = DiffResult(
        columns=["id"],
        added=[{"id": str(i)} for i in range(3)],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert out.count("added {") == 3


def test_special_characters_are_escaped():
    diff = DiffResult(
        columns=["id", "note"],
        added=[{"id": "1", "note": 'say "hello"'}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert '\\"hello\\"' in out
