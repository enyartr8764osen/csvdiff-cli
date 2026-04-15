"""Tests for csvdiff.render_ndjson."""

from __future__ import annotations

import io
import json
from typing import List

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_ndjson import render_ndjson


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _empty_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, changed={})


def _render(diff: DiffResult) -> List[dict]:
    """Render *diff* and parse every output line as JSON."""
    buf = io.StringIO()
    render_ndjson(diff, buf)
    lines = [l for l in buf.getvalue().splitlines() if l.strip()]
    return [json.loads(l) for l in lines]


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_no_changes_produces_no_output():
    records = _render(_empty_diff())
    assert records == []


def test_added_row_produces_added_record():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice"}
    records = _render(diff)
    assert len(records) == 1
    rec = records[0]
    assert rec["type"] == "added"
    assert rec["key"] == ["1"]
    assert rec["row"] == {"id": "1", "name": "Alice"}


def test_removed_row_produces_removed_record():
    diff = _empty_diff()
    diff.removed[("2",)] = {"id": "2", "name": "Bob"}
    records = _render(diff)
    assert len(records) == 1
    rec = records[0]
    assert rec["type"] == "removed"
    assert rec["key"] == ["2"]
    assert rec["row"] == {"id": "2", "name": "Bob"}


def test_changed_row_has_old_and_new():
    diff = _empty_diff()
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff.changed[("3",)] = (old, new)
    records = _render(diff)
    assert len(records) == 1
    rec = records[0]
    assert rec["type"] == "changed"
    assert rec["key"] == ["3"]
    assert rec["old"] == old
    assert rec["new"] == new
    assert "row" not in rec


def test_output_order_added_removed_changed():
    diff = _empty_diff()
    diff.added[("a",)] = {"id": "a"}
    diff.removed[("b",)] = {"id": "b"}
    diff.changed[("c",)] = ({"id": "c", "v": "1"}, {"id": "c", "v": "2"})
    records = _render(diff)
    assert [r["type"] for r in records] == ["added", "removed", "changed"]


def test_each_line_is_valid_json():
    diff = _empty_diff()
    diff.added[("x",)] = {"id": "x", "note": 'say \"hello\"'}
    diff.removed[("y",)] = {"id": "y", "note": "café"}
    buf = io.StringIO()
    render_ndjson(diff, buf)
    for line in buf.getvalue().splitlines():
        # Must not raise
        json.loads(line)


def test_composite_key_preserved_as_list():
    diff = _empty_diff()
    diff.added[("dept1", "emp42")] = {"dept": "dept1", "emp": "emp42", "role": "eng"}
    records = _render(diff)
    assert records[0]["key"] == ["dept1", "emp42"]
