"""Tests for csvdiff.render_sexp."""

from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_sexp import render_sexp, _escape, _quote, _row_to_sexp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_escape_plain_string_unchanged():
    assert _escape("hello") == "hello"


def test_escape_double_quote():
    assert _escape('say "hi"') == 'say \\"hi\\"'


def test_escape_backslash():
    assert _escape("a\\b") == "a\\\\b"


def test_quote_wraps_in_double_quotes():
    assert _quote("foo") == '"foo"'


def test_row_to_sexp_basic():
    row = {"id": "1", "name": "Alice"}
    result = _row_to_sexp(row, ["id", "name"])
    assert result == '(:id "1" :name "Alice")'


def test_row_to_sexp_missing_column_uses_empty_string():
    row = {"id": "7"}
    result = _row_to_sexp(row, ["id", "name"])
    assert ':name ""' in result


# ---------------------------------------------------------------------------
# render_sexp integration tests
# ---------------------------------------------------------------------------

def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_sexp(diff) == ""


def test_output_starts_with_csvdiff_form():
    result = render_sexp(_empty_diff())
    assert result.startswith("(csvdiff")


def test_output_ends_with_closing_paren():
    result = render_sexp(_empty_diff())
    assert result.rstrip().endswith(")")


def test_empty_diff_contains_three_sections():
    result = render_sexp(_empty_diff())
    assert "(added" in result
    assert "(removed" in result
    assert "(changed" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "2", "name": "Bob"}],
        removed=[],
        changed=[],
    )
    result = render_sexp(diff)
    added_block = result[result.index("(added"):result.index("(removed")]
    assert ':id "2"' in added_block
    assert ':name "Bob"' in added_block


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "3", "name": "Carol"}],
        changed=[],
    )
    result = render_sexp(diff)
    removed_block = result[result.index("(removed"):result.index("(changed")]
    assert ':name "Carol"' in removed_block


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[
            ({"id": "1", "name": "Alice"}, {"id": "1", "name": "Alicia"}),
        ],
    )
    result = render_sexp(diff)
    changed_block = result[result.index("(changed"):]
    assert "(change" in changed_block
    assert "(old " in changed_block
    assert "(new " in changed_block
    assert ':name "Alice"' in changed_block
    assert ':name "Alicia"' in changed_block
