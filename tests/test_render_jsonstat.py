"""Tests for csvdiff.render_jsonstat."""
from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonstat import render_jsonstat


def _empty_diff(columns=None):
    return DiffResult(
        columns=list(columns or ["id", "name"]),
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult) -> dict:
    buf = io.StringIO()
    render_jsonstat(diff, buf)
    return json.loads(buf.getvalue())


def test_empty_diff_is_valid_jsonstat():
    data = _render(_empty_diff())
    assert data["version"] == "2.0"
    assert data["class"] == "dataset"


def test_empty_diff_has_id_and_size():
    data = _render(_empty_diff())
    assert "id" in data
    assert "size" in data


def test_empty_diff_value_is_empty():
    data = _render(_empty_diff())
    assert data["value"] == []


def test_no_columns_returns_minimal_dataset():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    data = _render(diff)
    assert data["id"] == []
    assert data["size"] == []
    assert data["value"] == []


def test_added_row_appears_in_value():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    data = _render(diff)
    assert len(data["value"]) == 1
    assert data["value"][0] == ["1", "Alice"]


def test_added_row_status_is_added():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    data = _render(diff)
    assert data["extension"]["status_column"] == ["added"]


def test_removed_row_status_is_removed():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    data = _render(diff)
    assert data["extension"]["status_column"] == ["removed"]


def test_changed_row_produces_old_and_new_entries():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(
            {"id": "3", "name": "Carol"},
            {"id": "3", "name": "Caroline"},
        )],
    )
    data = _render(diff)
    statuses = data["extension"]["status_column"]
    assert "old" in statuses
    assert "new" in statuses
    assert len(statuses) == 2


def test_dimension_keys_include_status_and_columns():
    diff = DiffResult(
        columns=["id", "city"],
        added=[{"id": "5", "city": "Paris"}],
        removed=[],
        changed=[],
    )
    data = _render(diff)
    assert "status" in data["dimension"]
    assert "id" in data["dimension"]
    assert "city" in data["dimension"]


def test_ids_start_with_status():
    data = _render(_empty_diff(["x", "y"]))
    assert data["id"][0] == "status"
    assert "x" in data["id"]
    assert "y" in data["id"]
