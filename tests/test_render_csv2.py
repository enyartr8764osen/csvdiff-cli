"""Tests for csvdiff.render_csv2."""
from __future__ import annotations

import csv
import io
from typing import Dict, List

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_csv2 import render_csv2


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        key_columns=["id"],
        added={},
        removed={},
        changed={},
    )


def _parse(text: str) -> List[Dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


# ---------------------------------------------------------------------------
# No changes
# ---------------------------------------------------------------------------

def test_no_changes_produces_header_only():
    result = render_csv2(_empty_diff())
    rows = _parse(result)
    assert rows == []


def test_no_changes_header_contains_status():
    result = render_csv2(_empty_diff())
    first_line = result.splitlines()[0]
    assert first_line.startswith("status")


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], key_columns=[], added={}, removed={}, changed={})
    assert render_csv2(diff) == ""


# ---------------------------------------------------------------------------
# Added rows
# ---------------------------------------------------------------------------

def test_added_row_has_added_status():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice"}
    rows = _parse(render_csv2(diff))
    assert len(rows) == 1
    assert rows[0]["status"] == "added"
    assert rows[0]["name"] == "Alice"


# ---------------------------------------------------------------------------
# Removed rows
# ---------------------------------------------------------------------------

def test_removed_row_has_removed_status():
    diff = _empty_diff()
    diff.removed[("2",)] = {"id": "2", "name": "Bob"}
    rows = _parse(render_csv2(diff))
    assert rows[0]["status"] == "removed"
    assert rows[0]["name"] == "Bob"


# ---------------------------------------------------------------------------
# Changed rows
# ---------------------------------------------------------------------------

def test_changed_row_produces_two_rows():
    diff = _empty_diff()
    diff.changed[("3",)] = ({"id": "3", "name": "Old"}, {"id": "3", "name": "New"})
    rows = _parse(render_csv2(diff))
    assert len(rows) == 2
    statuses = {r["status"] for r in rows}
    assert statuses == {"changed", "changed_new"}


def test_changed_row_old_and_new_values():
    diff = _empty_diff()
    diff.changed[("3",)] = ({"id": "3", "name": "Old"}, {"id": "3", "name": "New"})
    rows = _parse(render_csv2(diff))
    old = next(r for r in rows if r["status"] == "changed")
    new = next(r for r in rows if r["status"] == "changed_new")
    assert old["name"] == "Old"
    assert new["name"] == "New"


# ---------------------------------------------------------------------------
# Key column
# ---------------------------------------------------------------------------

def test_include_key_false_omits_key_column():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice"}
    result = render_csv2(diff, include_key=False)
    rows = _parse(result)
    assert "_key" not in rows[0]


def test_include_key_true_adds_key_column():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice"}
    rows = _parse(render_csv2(diff, include_key=True))
    assert "_key" in rows[0]
    assert rows[0]["_key"] == "1"


# ---------------------------------------------------------------------------
# Custom delimiter
# ---------------------------------------------------------------------------

def test_custom_delimiter_tab():
    diff = _empty_diff()
    diff.added[("1",)] = {"id": "1", "name": "Alice"}
    result = render_csv2(diff, delimiter="\t")
    first_line = result.splitlines()[0]
    assert "\t" in first_line
    assert "," not in first_line
