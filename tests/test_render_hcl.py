"""Tests for csvdiff.render_hcl."""

from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_hcl import _escape, render_hcl


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_hcl(diff, buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# _escape
# ---------------------------------------------------------------------------

def test_escape_plain_string_unchanged():
    assert _escape("hello") == "hello"


def test_escape_double_quote():
    assert _escape('say "hi"') == 'say \\"hi\\"'


def test_escape_backslash():
    assert _escape("a\\b") == "a\\\\b"


def test_escape_newline():
    assert _escape("line1\nline2") == "line1\\nline2"


# ---------------------------------------------------------------------------
# render_hcl
# ---------------------------------------------------------------------------

def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert _render(diff) == ""


def test_empty_diff_has_three_sections():
    output = _render(_empty_diff())
    assert "added {" in output
    assert "removed {" in output
    assert "changed {" in output


def test_empty_sections_have_comment():
    output = _render(_empty_diff())
    assert output.count("# no rows") == 3


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    output = _render(diff)
    assert 'id = "1"' in output
    assert 'name = "Alice"' in output
    # ensure it is inside the added block
    added_start = output.index("added {")
    removed_start = output.index("removed {")
    assert added_start < output.index('name = "Alice"') < removed_start


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    output = _render(diff)
    assert 'name = "Bob"' in output


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(
            {"id": "3", "name": "Carol"},
            {"id": "3", "name": "Caroline"},
        )],
    )
    output = _render(diff)
    assert "old {" in output
    assert "new {" in output
    assert 'name = "Carol"' in output
    assert 'name = "Caroline"' in output


def test_row_block_labels_are_zero_based_indices():
    diff = DiffResult(
        columns=["id"],
        added=[{"id": "a"}, {"id": "b"}],
        removed=[],
        changed=[],
    )
    output = _render(diff)
    assert 'row "0"' in output
    assert 'row "1"' in output
