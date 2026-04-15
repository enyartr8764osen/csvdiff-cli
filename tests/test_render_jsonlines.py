"""Tests for csvdiff.render_jsonlines."""

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonlines import render_jsonlines


def _empty_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, changed={}, columns=["id", "name", "value"])


def _parse(output: str) -> list[dict]:
    """Parse JSON Lines output into a list of dicts."""
    return [json.loads(line) for line in output.strip().splitlines() if line.strip()]


def test_no_changes_produces_no_output():
    out = io.StringIO()
    render_jsonlines(_empty_diff(), out)
    assert out.getvalue() == ""


def test_added_row_produces_added_record():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice", "value": "10"}
    out = io.StringIO()
    render_jsonlines(diff, out)
    records = _parse(out.getvalue())
    assert len(records) == 1
    assert records[0]["type"] == "added"
    assert records[0]["key"] == ["1"]
    assert records[0]["row"] == {"id": "1", "name": "Alice", "value": "10"}


def test_removed_row_produces_removed_record():
    diff = _empty_diff()
    diff.removed[("2",)] = {"id": "2", "name": "Bob", "value": "20"}
    out = io.StringIO()
    render_jsonlines(diff, out)
    records = _parse(out.getvalue())
    assert len(records) == 1
    assert records[0]["type"] == "removed"
    assert records[0]["key"] == ["2"]
    assert records[0]["row"] == {"id": "2", "name": "Bob", "value": "20"}


def test_changed_row_includes_fields_list():
    diff = _empty_diff()
    old = {"id": "3", "name": "Carol", "value": "30"}
    new = {"id": "3", "name": "Carol", "value": "99"}
    diff.changed[("3",)] = (old, new)
    out = io.StringIO()
    render_jsonlines(diff, out)
    records = _parse(out.getvalue())
    assert len(records) == 1
    r = records[0]
    assert r["type"] == "changed"
    assert r["key"] == ["3"]
    assert r["old"] == old
    assert r["new"] == new
    assert r["fields"] == ["value"]


def test_multiple_changes_each_on_own_line():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice", "value": "10"}
    diff.removed[("2",)] = {"id": "2", "name": "Bob", "value": "20"}
    diff.changed[("3",)] = (
        {"id": "3", "name": "Carol", "value": "30"},
        {"id": "3", "name": "Carol", "value": "31"},
    )
    out = io.StringIO()
    render_jsonlines(diff, out)
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    assert len(lines) == 3
    # Every line must be valid JSON
    for line in lines:
        obj = json.loads(line)
        assert "type" in obj


def test_unicode_values_are_preserved():
    diff = _empty_diff()
    diff.added[("\u4e2d",)] = {"id": "\u4e2d", "name": "\u6587", "value": "\u5b57"}
    out = io.StringIO()
    render_jsonlines(diff, out)
    records = _parse(out.getvalue())
    assert records[0]["row"]["name"] == "\u6587"
