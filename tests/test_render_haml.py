"""Tests for csvdiff.render_haml."""

from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_haml import render_haml, _escape


def _empty_diff(columns=None):
    return DiffResult(
        columns=columns or ["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


# ---------------------------------------------------------------------------
# _escape
# ---------------------------------------------------------------------------

def test_escape_ampersand():
    assert _escape("a & b") == "a &amp; b"


def test_escape_less_than():
    assert _escape("a < b") == "a &lt; b"


def test_escape_greater_than():
    assert _escape("a > b") == "a &gt; b"


def test_escape_quote():
    assert _escape('say "hi"') == "say &quot;hi&quot;"


def test_escape_plain_unchanged():
    assert _escape("hello") == "hello"


# ---------------------------------------------------------------------------
# no changes
# ---------------------------------------------------------------------------

def test_no_changes_produces_no_differences_message():
    out = render_haml(_empty_diff())
    assert "No differences found" in out


def test_no_columns_returns_empty_string():
    diff = _empty_diff(columns=[])
    assert render_haml(diff) == ""


def test_root_element_present():
    out = render_haml(_empty_diff())
    assert out.startswith("%div.csvdiff")


# ---------------------------------------------------------------------------
# added rows
# ---------------------------------------------------------------------------

def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = render_haml(diff)
    assert ".section.added" in out
    assert "Alice" in out
    assert "%th id" in out


def test_added_section_has_table_structure():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "2", "name": "Bob"}],
        removed=[],
        changed=[],
    )
    out = render_haml(diff)
    assert "%table" in out
    assert "%thead" in out
    assert "%tbody" in out
    assert "%tr" in out
    assert "%td Bob" in out


# ---------------------------------------------------------------------------
# removed rows
# ---------------------------------------------------------------------------

def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "3", "name": "Carol"}],
        changed=[],
    )
    out = render_haml(diff)
    assert ".section.removed" in out
    assert "Carol" in out


# ---------------------------------------------------------------------------
# changed rows
# ---------------------------------------------------------------------------

def test_changed_row_shows_before_and_after():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[
            {"old": {"id": "4", "name": "Dave"}, "new": {"id": "4", "name": "David"}}
        ],
    )
    out = render_haml(diff)
    assert "Changed (before)" in out
    assert "Changed (after)" in out
    assert "Dave" in out
    assert "David" in out
