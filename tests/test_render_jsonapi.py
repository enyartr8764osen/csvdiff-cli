"""Tests for csvdiff.render_jsonapi."""
from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonapi import render_jsonapi


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[], columns=[])


def _render(diff: DiffResult, indent: int = 2) -> dict:
    buf = io.StringIO()
    render_jsonapi(diff, buf, indent=indent)
    return json.loads(buf.getvalue())


def test_empty_diff_has_data_and_meta():
    doc = _render(_empty_diff())
    assert "data" in doc
    assert "meta" in doc


def test_empty_diff_data_is_empty_list():
    doc = _render(_empty_diff())
    assert doc["data"] == []


def test_empty_diff_meta_counts_are_zero():
    doc = _render(_empty_diff())
    assert doc["meta"]["added"] == 0
    assert doc["meta"]["removed"] == 0
    assert doc["meta"]["changed"] == 0
    assert doc["meta"]["total"] == 0


def test_added_row_appears_in_data():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
        columns=["id", "name"],
    )
    doc = _render(diff)
    assert len(doc["data"]) == 1
    resource = doc["data"][0]
    assert resource["type"] == "added"
    assert resource["attributes"] == {"id": "1", "name": "Alice"}


def test_removed_row_appears_in_data():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
        columns=["id", "name"],
    )
    doc = _render(diff)
    assert len(doc["data"]) == 1
    resource = doc["data"][0]
    assert resource["type"] == "removed"
    assert resource["attributes"] == {"id": "2", "name": "Bob"}


def test_changed_row_has_before_and_after():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        added=[],
        removed=[],
        changed=[(old, new)],
        columns=["id", "name"],
    )
    doc = _render(diff)
    assert len(doc["data"]) == 1
    resource = doc["data"][0]
    assert resource["type"] == "changed"
    assert resource["attributes"]["before"] == old
    assert resource["attributes"]["after"] == new


def test_changed_row_lists_changed_fields():
    old = {"id": "3", "name": "Carol", "age": "30"}
    new = {"id": "3", "name": "Caroline", "age": "30"}
    diff = DiffResult(
        added=[],
        removed=[],
        changed=[(old, new)],
        columns=["id", "name", "age"],
    )
    doc = _render(diff)
    changed_fields = doc["data"][0]["attributes"]["changed_fields"]
    assert changed_fields == ["name"]


def test_meta_total_reflects_all_entries():
    diff = DiffResult(
        added=[{"id": "1", "v": "a"}],
        removed=[{"id": "2", "v": "b"}],
        changed=[({"id": "3", "v": "c"}, {"id": "3", "v": "d"})],
        columns=["id", "v"],
    )
    doc = _render(diff)
    assert doc["meta"]["total"] == 3
    assert doc["meta"]["added"] == 1
    assert doc["meta"]["removed"] == 1
    assert doc["meta"]["changed"] == 1


def test_output_ends_with_newline():
    buf = io.StringIO()
    render_jsonapi(_empty_diff(), buf)
    assert buf.getvalue().endswith("\n")
