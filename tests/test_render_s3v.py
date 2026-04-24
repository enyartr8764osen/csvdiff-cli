"""Tests for csvdiff.render_s3v."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_s3v import render_s3v, _quote, _row_to_sexp


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_s3v(diff, buf)
    return buf.getvalue()


# ── _quote ────────────────────────────────────────────────────────────────────

def test_quote_plain_string():
    assert _quote("hello") == '"hello"'


def test_quote_escapes_double_quote():
    assert _quote('say "hi"') == '"say \\"hi\\""'


def test_quote_escapes_backslash():
    assert _quote('a\\b') == '"a\\\\b"'


# ── _row_to_sexp ──────────────────────────────────────────────────────────────

def test_row_to_sexp_single_pair():
    result = _row_to_sexp({"id": "1"})
    assert result == '(("id" . "1"))'


def test_row_to_sexp_multiple_pairs():
    result = _row_to_sexp({"id": "1", "name": "Alice"})
    assert '("id" . "1")' in result
    assert '("name" . "Alice")' in result


# ── render_s3v ────────────────────────────────────────────────────────────────

def test_no_columns_produces_no_output():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert _render(diff) == ""


def test_empty_diff_has_root_element():
    output = _render(_empty_diff())
    assert output.startswith("(csvdiff")
    assert output.strip().endswith(")")


def test_empty_diff_has_three_sections():
    output = _render(_empty_diff())
    assert "(added" in output
    assert "(removed" in output
    assert "(changed" in output


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    output = _render(diff)
    added_start = output.index("(added")
    added_end = output.index("(removed")
    added_section = output[added_start:added_end]
    assert '"Alice"' in added_section


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    output = _render(diff)
    removed_start = output.index("(removed")
    removed_end = output.index("(changed")
    removed_section = output[removed_start:removed_end]
    assert '"Bob"' in removed_section


def test_changed_row_new_values_appear_in_changed_section():
    diff = DiffResult(
        columns=["id", "val"],
        added=[],
        removed=[],
        changed=[({"id": "3", "val": "old"}, {"id": "3", "val": "new"})],
    )
    output = _render(diff)
    changed_start = output.index("(changed")
    changed_section = output[changed_start:]
    assert '"new"' in changed_section
