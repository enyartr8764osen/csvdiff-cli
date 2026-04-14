"""Tests for csvdiff.render_csv module."""

import csv
import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_csv import render_csv, STATUS_COLUMN


def _parse(text: str) -> list:
    """Parse CSV text into a list of dicts."""
    return list(csv.DictReader(io.StringIO(text)))


def _empty_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


def test_render_csv_no_changes_produces_no_output():
    out = io.StringIO()
    render_csv(_empty_diff(), out)
    assert out.getvalue() == ""


def test_render_csv_added_row():
    diff = DiffResult(
        added={("3",): {"id": "3", "name": "Carol"}},
        removed={},
        modified={},
    )
    out = io.StringIO()
    render_csv(diff, out)
    rows = _parse(out.getvalue())
    assert len(rows) == 1
    assert rows[0][STATUS_COLUMN] == "added"
    assert rows[0]["name"] == "Carol"


def test_render_csv_removed_row():
    diff = DiffResult(
        added={},
        removed={("1",): {"id": "1", "name": "Alice"}},
        modified={},
    )
    out = io.StringIO()
    render_csv(diff, out)
    rows = _parse(out.getvalue())
    assert rows[0][STATUS_COLUMN] == "removed"
    assert rows[0]["id"] == "1"


def test_render_csv_modified_row_splits_changed_columns():
    old = {"id": "2", "name": "Bob", "dept": "hr"}
    new = {"id": "2", "name": "Robert", "dept": "hr"}
    diff = DiffResult(
        added={},
        removed={},
        modified={("2",): (old, new)},
    )
    out = io.StringIO()
    render_csv(diff, out)
    rows = _parse(out.getvalue())
    assert len(rows) == 1
    row = rows[0]
    assert row[STATUS_COLUMN] == "modified"
    assert row["name_old"] == "Bob"
    assert row["name_new"] == "Robert"
    # Unchanged column should appear without suffix
    assert row["dept"] == "hr"


def test_render_csv_custom_delimiter():
    diff = DiffResult(
        added={("5",): {"id": "5", "val": "x"}},
        removed={},
        modified={},
    )
    out = io.StringIO()
    render_csv(diff, out, delimiter=";")
    first_line = out.getvalue().splitlines()[0]
    assert ";" in first_line
    assert "," not in first_line
