"""Tests for csvdiff.render_jsonl."""

from __future__ import annotations

import json
from io import StringIO

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonl import render_jsonl


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _render(diff: DiffResult, key_cols=None) -> list[dict]:
    """Render *diff* and return parsed JSON objects."""
    if key_cols is None:
        key_cols = ["id"]
    raw = render_jsonl(diff, key_cols)
    if not raw.strip():
        return []
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_no_changes_produces_no_output():
    records = _render(_empty_diff())
    assert records == []


def test_added_row_produces_added_record():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    records = _render(diff, key_cols=["id"])
    assert len(records) == 1
    rec = records[0]
    assert rec["status"] == "added"
    assert rec["key"] == {"id": "1"}
    assert rec["row"] == {"id": "1", "name": "Alice"}


def test_removed_row_produces_removed_record():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    records = _render(diff, key_cols=["id"])
    assert len(records) == 1
    rec = records[0]
    assert rec["status"] == "removed"
    assert rec["key"] == {"id": "2"}
    assert rec["row"] == {"id": "2", "name": "Bob"}


def test_changed_row_produces_changed_record():
    before = {"id": "3", "name": "Carol"}
    after = {"id": "3", "name": "Caroline"}
    diff = DiffResult(added=[], removed=[], changed=[(before, after)])
    records = _render(diff, key_cols=["id"])
    assert len(records) == 1
    rec = records[0]
    assert rec["status"] == "changed"
    assert rec["key"] == {"id": "3"}
    assert rec["before"] == before
    assert rec["after"] == after


def test_multiple_events_order_added_removed_changed():
    diff = DiffResult(
        added=[{"id": "10", "v": "x"}],
        removed=[{"id": "20", "v": "y"}],
        changed=[({"id": "30", "v": "a"}, {"id": "30", "v": "b"})],
    )
    records = _render(diff, key_cols=["id"])
    statuses = [r["status"] for r in records]
    assert statuses == ["added", "removed", "changed"]


def test_stream_receives_output():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    buf = StringIO()
    result = render_jsonl(diff, ["id"], stream=buf)
    assert buf.getvalue() == result
    assert len(result.strip().splitlines()) == 1


def test_compound_key_all_key_cols_included():
    row = {"a": "1", "b": "2", "c": "val"}
    diff = DiffResult(added=[row], removed=[], changed=[])
    records = _render(diff, key_cols=["a", "b"])
    assert records[0]["key"] == {"a": "1", "b": "2"}


def test_each_line_is_valid_json():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    raw = render_jsonl(diff, ["id"])
    for line in raw.splitlines():
        parsed = json.loads(line)  # must not raise
        assert isinstance(parsed, dict)
