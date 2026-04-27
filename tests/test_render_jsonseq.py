"""Tests for csvdiff.render_jsonseq."""
from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonseq import _RS, render_jsonseq


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added={}, removed={}, changed={})


def _render(diff: DiffResult, **kwargs) -> list[dict]:
    """Render *diff* and parse each RS-delimited record back to a dict."""
    buf = io.StringIO()
    render_jsonseq(diff, buf, **kwargs)
    text = buf.getvalue()
    records = []
    for chunk in text.split(_RS):
        chunk = chunk.strip()
        if chunk:
            records.append(json.loads(chunk))
    return records


def test_no_changes_produces_no_output():
    records = _render(_empty_diff())
    assert records == []


def test_added_row_produces_added_record():
    diff = DiffResult(
        columns=["id", "name"],
        added={("1",): {"id": "1", "name": "Alice"}},
        removed={},
        changed={},
    )
    records = _render(diff)
    assert len(records) == 1
    assert records[0]["_status"] == "added"
    assert records[0]["id"] == "1"
    assert records[0]["name"] == "Alice"


def test_removed_row_produces_removed_record():
    diff = DiffResult(
        columns=["id", "name"],
        added={},
        removed={("2",): {"id": "2", "name": "Bob"}},
        changed={},
    )
    records = _render(diff)
    assert len(records) == 1
    assert records[0]["_status"] == "removed"
    assert records[0]["id"] == "2"


def test_changed_row_produces_changed_record_with_before_and_after():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        columns=["id", "name"],
        added={},
        removed={},
        changed={("3",): (old, new)},
    )
    records = _render(diff)
    assert len(records) == 1
    rec = records[0]
    assert rec["_status"] == "changed"
    assert rec["_before"] == old
    assert rec["_after"] == new


def test_each_record_prefixed_with_rs():
    diff = DiffResult(
        columns=["id", "name"],
        added={("1",): {"id": "1", "name": "Alice"}},
        removed={("2",): {"id": "2", "name": "Bob"}},
        changed={},
    )
    buf = io.StringIO()
    render_jsonseq(diff, buf)
    raw = buf.getvalue()
    # Every record must start with RS
    assert raw.count(_RS) == 2
    for segment in raw.split(_RS):
        stripped = segment.strip()
        if stripped:
            json.loads(stripped)  # must be valid JSON


def test_each_record_terminated_with_newline():
    diff = DiffResult(
        columns=["id"],
        added={("1",): {"id": "1"}},
        removed={},
        changed={},
    )
    buf = io.StringIO()
    render_jsonseq(diff, buf)
    raw = buf.getvalue()
    # After stripping RS the line should end with newline
    assert raw.endswith("\n")


def test_indent_parameter_formats_json():
    diff = DiffResult(
        columns=["id"],
        added={("1",): {"id": "1"}},
        removed={},
        changed={},
    )
    records_compact = _render(diff)
    buf = io.StringIO()
    render_jsonseq(diff, buf, indent=2)
    raw_indented = buf.getvalue()
    # Indented output should contain newlines within the JSON object
    assert "\n" in raw_indented.replace(_RS, "")
    # But still parse to the same data
    records_indented = _render(diff, indent=2)
    assert records_compact == records_indented
