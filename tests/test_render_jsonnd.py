"""Tests for csvdiff.render_jsonnd."""
from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonnd import render_jsonnd, _key_to_obj


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def _render(diff: DiffResult, **kwargs) -> list[dict]:
    buf = io.StringIO()
    render_jsonnd(diff, buf, **kwargs)
    text = buf.getvalue().strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


# ---------------------------------------------------------------------------
# _key_to_obj
# ---------------------------------------------------------------------------

def test_key_to_obj_with_columns():
    assert _key_to_obj(("1",), ["id"]) == {"id": "1"}


def test_key_to_obj_without_columns():
    assert _key_to_obj(("a", "b"), []) == {"0": "a", "1": "b"}


# ---------------------------------------------------------------------------
# Empty diff
# ---------------------------------------------------------------------------

def test_no_changes_produces_no_output():
    records = _render(_empty_diff())
    assert records == []


# ---------------------------------------------------------------------------
# Added rows
# ---------------------------------------------------------------------------

def test_added_row_produces_added_record():
    diff = DiffResult(
        columns=["id", "name"],
        added=[(("1",), ("1", "Alice"))],
        removed=[],
        changed=[],
    )
    records = _render(diff, key_columns=["id"])
    assert len(records) == 1
    assert records[0]["status"] == "added"
    assert records[0]["key"] == {"id": "1"}
    assert records[0]["row"] == {"id": "1", "name": "Alice"}


# ---------------------------------------------------------------------------
# Removed rows
# ---------------------------------------------------------------------------

def test_removed_row_produces_removed_record():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[(("2",), ("2", "Bob"))],
        changed=[],
    )
    records = _render(diff, key_columns=["id"])
    assert len(records) == 1
    assert records[0]["status"] == "removed"
    assert records[0]["row"] == {"id": "2", "name": "Bob"}


# ---------------------------------------------------------------------------
# Changed rows
# ---------------------------------------------------------------------------

def test_changed_row_produces_changed_record():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(("3",), ("3", "Carol"), ("3", "Caroline"))],
    )
    records = _render(diff, key_columns=["id"])
    assert len(records) == 1
    rec = records[0]
    assert rec["status"] == "changed"
    assert rec["old"] == {"id": "3", "name": "Carol"}
    assert rec["new"] == {"id": "3", "name": "Caroline"}
    assert "row" not in rec


# ---------------------------------------------------------------------------
# Multiple changes — order: added, removed, changed
# ---------------------------------------------------------------------------

def test_ordering_is_added_removed_changed():
    diff = DiffResult(
        columns=["id", "name"],
        added=[(("1",), ("1", "Alice"))],
        removed=[(("2",), ("2", "Bob"))],
        changed=[(("3",), ("3", "Carol"), ("3", "Caroline"))],
    )
    records = _render(diff, key_columns=["id"])
    assert [r["status"] for r in records] == ["added", "removed", "changed"]


# ---------------------------------------------------------------------------
# Each line is valid JSON
# ---------------------------------------------------------------------------

def test_each_line_is_valid_json():
    diff = DiffResult(
        columns=["id", "value"],
        added=[(("10",), ("10", "x"))],
        removed=[(("20",), ("20", "y"))],
        changed=[],
    )
    buf = io.StringIO()
    render_jsonnd(diff, buf, key_columns=["id"])
    for line in buf.getvalue().splitlines():
        json.loads(line)  # must not raise
