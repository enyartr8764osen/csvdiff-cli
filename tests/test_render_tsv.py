"""Tests for csvdiff.render_tsv."""

from __future__ import annotations

import csv
import io
from typing import Dict, List

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_tsv import render_tsv


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _parse(tsv_text: str) -> List[Dict[str, str]]:
    """Parse TSV output into a list of dicts."""
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    return list(reader)


COLS = ["id", "name", "value"]


def test_no_changes_produces_empty_string():
    result = render_tsv(_empty_diff(), COLS)
    assert result == ""


def test_added_row_has_added_status():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice", "value": "10"}],
        removed=[],
        changed=[],
    )
    rows = _parse(render_tsv(diff, COLS))
    assert len(rows) == 1
    assert rows[0]["_status"] == "added"
    assert rows[0]["id"] == "1"
    assert rows[0]["name"] == "Alice"


def test_removed_row_has_removed_status():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob", "value": "20"}],
        changed=[],
    )
    rows = _parse(render_tsv(diff, COLS))
    assert len(rows) == 1
    assert rows[0]["_status"] == "removed"
    assert rows[0]["id"] == "2"


def test_changed_row_produces_two_rows():
    old = {"id": "3", "name": "Carol", "value": "30"}
    new = {"id": "3", "name": "Carol", "value": "99"}
    diff = DiffResult(added=[], removed=[], changed=[(old, new)])
    rows = _parse(render_tsv(diff, COLS))
    assert len(rows) == 2
    statuses = [r["_status"] for r in rows]
    assert "changed_old" in statuses
    assert "changed_new" in statuses
    old_row = next(r for r in rows if r["_status"] == "changed_old")
    new_row = next(r for r in rows if r["_status"] == "changed_new")
    assert old_row["value"] == "30"
    assert new_row["value"] == "99"


def test_header_contains_status_column():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice", "value": "10"}],
        removed=[],
        changed=[],
    )
    tsv_text = render_tsv(diff, COLS)
    first_line = tsv_text.splitlines()[0]
    assert first_line.startswith("_status\t")


def test_missing_column_value_defaults_to_empty_string():
    diff = DiffResult(
        added=[{"id": "5", "name": "Eve"}],  # 'value' key missing
        removed=[],
        changed=[],
    )
    rows = _parse(render_tsv(diff, COLS))
    assert rows[0]["value"] == ""


def test_multiple_added_rows():
    diff = DiffResult(
        added=[
            {"id": "1", "name": "A", "value": "1"},
            {"id": "2", "name": "B", "value": "2"},
        ],
        removed=[],
        changed=[],
    )
    rows = _parse(render_tsv(diff, COLS))
    assert len(rows) == 2
    assert all(r["_status"] == "added" for r in rows)
