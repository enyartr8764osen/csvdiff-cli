"""Tests for csvdiff.render_csv3."""
from __future__ import annotations

import csv
import io
from typing import Dict, List

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_csv3 import render_csv3


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _parse(text: str) -> List[Dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def test_no_columns_returns_empty_string():
    assert render_csv3(_empty_diff(), []) == ""


def test_no_changes_produces_header_only():
    result = render_csv3(_empty_diff(), ["id", "name"])
    rows = _parse(result)
    assert rows == []
    # Header must still be present
    assert "_status" in result
    assert "id" in result
    assert "name" in result


def test_added_row_has_added_status():
    diff = DiffResult(added=[{"id": "1", "name": "Alice"}], removed=[], changed=[])
    rows = _parse(render_csv3(diff, ["id", "name"]))
    assert len(rows) == 1
    assert rows[0]["_status"] == "added"
    assert rows[0]["id"] == "1"
    assert rows[0]["name"] == "Alice"


def test_removed_row_has_removed_status():
    diff = DiffResult(added=[], removed=[{"id": "2", "name": "Bob"}], changed=[])
    rows = _parse(render_csv3(diff, ["id", "name"]))
    assert len(rows) == 1
    assert rows[0]["_status"] == "removed"
    assert rows[0]["id"] == "2"


def test_changed_row_produces_two_rows():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(added=[], removed=[], changed=[(old, new)])
    rows = _parse(render_csv3(diff, ["id", "name"]))
    assert len(rows) == 2
    statuses = [r["_status"] for r in rows]
    assert "changed:before" in statuses
    assert "changed:after" in statuses


def test_changed_before_row_has_old_values():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(added=[], removed=[], changed=[(old, new)])
    rows = _parse(render_csv3(diff, ["id", "name"]))
    before = next(r for r in rows if r["_status"] == "changed:before")
    assert before["name"] == "Carol"


def test_changed_after_row_has_new_values():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(added=[], removed=[], changed=[(old, new)])
    rows = _parse(render_csv3(diff, ["id", "name"]))
    after = next(r for r in rows if r["_status"] == "changed:after")
    assert after["name"] == "Caroline"


def test_custom_delimiter():
    diff = DiffResult(added=[{"id": "1", "val": "x"}], removed=[], changed=[])
    result = render_csv3(diff, ["id", "val"], delimiter=";")
    assert ";" in result
    rows = list(csv.DictReader(io.StringIO(result), delimiter=";"))
    assert rows[0]["_status"] == "added"


def test_missing_column_value_defaults_to_empty_string():
    diff = DiffResult(added=[{"id": "9"}], removed=[], changed=[])
    rows = _parse(render_csv3(diff, ["id", "name"]))
    assert rows[0]["name"] == ""
