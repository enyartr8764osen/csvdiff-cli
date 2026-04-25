"""Tests for render_textile2."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_textile2 import render_textile2


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
        unchanged=[],
    )


def _render(diff: DiffResult, **kwargs: object) -> str:
    buf = io.StringIO()
    render_textile2(diff, buf, **kwargs)  # type: ignore[arg-type]
    return buf.getvalue()


def test_no_columns_returns_empty_string() -> None:
    diff = DiffResult(columns=[], added=[], removed=[], changed=[], unchanged=[])
    assert _render(diff) == ""


def test_no_changes_produces_no_differences_message() -> None:
    out = _render(_empty_diff())
    assert "No differences" in out


def test_added_row_appears_in_added_section() -> None:
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    out = _render(diff)
    assert "Added" in out
    assert "Alice" in out


def test_added_row_has_added_marker() -> None:
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    out = _render(diff)
    assert "+added+" in out


def test_removed_row_appears_in_removed_section() -> None:
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob"})
    out = _render(diff)
    assert "Removed" in out
    assert "Bob" in out


def test_removed_row_has_removed_marker() -> None:
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob"})
    out = _render(diff)
    assert "-removed-" in out


def test_changed_row_shows_before_and_after() -> None:
    diff = _empty_diff()
    diff.changed.append((
        {"id": "3", "name": "Old"},
        {"id": "3", "name": "New"},
    ))
    out = _render(diff)
    assert "Changed" in out
    assert "Before" in out
    assert "After" in out
    assert "Old" in out
    assert "New" in out


def test_changed_row_has_before_and_after_markers() -> None:
    diff = _empty_diff()
    diff.changed.append((
        {"id": "3", "name": "Old"},
        {"id": "3", "name": "New"},
    ))
    out = _render(diff)
    assert "~before~" in out
    assert "*after*" in out


def test_header_row_uses_bold_textile_syntax() -> None:
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    out = _render(diff)
    # Textile bold header cells use |_. *col* | syntax
    assert "|_." in out
    assert "*id*" in out
    assert "*name*" in out


def test_change_column_in_header() -> None:
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    out = _render(diff)
    assert "*change*" in out
