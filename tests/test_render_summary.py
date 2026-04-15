"""Tests for csvdiff.render_summary."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_summary import render_summary


def _empty_diff() -> DiffResult:
    return {"added": [], "removed": [], "changed": []}


def _capture(diff: DiffResult, **kwargs) -> str:
    buf = io.StringIO()
    render_summary(diff, buf, **kwargs)
    return buf.getvalue()


def test_no_changes_prints_no_differences():
    out = _capture(_empty_diff())
    assert "No differences found" in out


def test_added_rows_reported():
    diff = _empty_diff()
    diff["added"] = [{"id": "1", "name": "Alice"}]
    out = _capture(diff)
    assert "1 added" in out
    assert "removed" not in out
    assert "changed" not in out


def test_removed_rows_reported():
    diff = _empty_diff()
    diff["removed"] = [{"id": "2", "name": "Bob"}]
    out = _capture(diff)
    assert "1 removed" in out


def test_changed_rows_reported():
    diff = _empty_diff()
    diff["changed"] = [
        {"key": ("3",), "old": {"id": "3", "val": "x"}, "new": {"id": "3", "val": "y"}}
    ]
    out = _capture(diff)
    assert "1 changed" in out


def test_all_three_present():
    diff: DiffResult = {
        "added": [{"id": "1"}],
        "removed": [{"id": "2"}],
        "changed": [
            {"key": ("3",), "old": {"id": "3", "v": "a"}, "new": {"id": "3", "v": "b"}}
        ],
    }
    out = _capture(diff)
    assert "1 added" in out
    assert "1 removed" in out
    assert "1 changed" in out
    assert "(3 rows affected)" in out


def test_plural_rows_note():
    diff = _empty_diff()
    diff["added"] = [{"id": str(i)} for i in range(3)]
    out = _capture(diff)
    assert "(3 rows affected)" in out


def test_singular_row_note():
    diff = _empty_diff()
    diff["removed"] = [{"id": "9"}]
    out = _capture(diff)
    assert "(1 row affected)" in out


def test_color_flag_adds_ansi_codes():
    diff = _empty_diff()
    diff["added"] = [{"id": "1"}]
    out = _capture(diff, color=True)
    assert "\033[" in out


def test_no_color_no_ansi_codes():
    diff = _empty_diff()
    diff["added"] = [{"id": "1"}]
    out = _capture(diff, color=False)
    assert "\033[" not in out
