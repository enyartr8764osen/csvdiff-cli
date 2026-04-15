"""Tests for csvdiff.render_sql."""
from __future__ import annotations

import io
from typing import Dict, List

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_sql import render_sql


def _empty_diff(columns: List[str] | None = None) -> DiffResult:
    return DiffResult(
        columns=columns or ["id", "name", "value"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult, table: str = "mytable", keys: List[str] | None = None) -> str:
    buf = io.StringIO()
    render_sql(diff, table=table, out=buf, key_columns=keys or ["id"])
    return buf.getvalue()


# ---------------------------------------------------------------------------
# No changes
# ---------------------------------------------------------------------------

def test_no_changes_produces_no_output():
    assert _render(_empty_diff()) == ""


def test_no_columns_produces_no_output():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert _render(diff) == ""


# ---------------------------------------------------------------------------
# Added rows
# ---------------------------------------------------------------------------

def test_added_row_produces_insert():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "42"})
    sql = _render(diff)
    assert sql.startswith("INSERT INTO mytable")
    assert "'Alice'" in sql
    assert "'42'" in sql


def test_added_row_insert_contains_all_columns():
    diff = _empty_diff()
    diff.added.append({"id": "2", "name": "Bob", "value": "99"})
    sql = _render(diff)
    assert "id, name, value" in sql
    assert "VALUES ('2', 'Bob', '99')" in sql


# ---------------------------------------------------------------------------
# Removed rows
# ---------------------------------------------------------------------------

def test_removed_row_produces_delete():
    diff = _empty_diff()
    diff.removed.append({"id": "3", "name": "Carol", "value": "7"})
    sql = _render(diff)
    assert "DELETE FROM mytable" in sql
    assert "WHERE id = '3'" in sql


# ---------------------------------------------------------------------------
# Changed rows
# ---------------------------------------------------------------------------

def test_changed_row_produces_update():
    diff = _empty_diff()
    old = {"id": "4", "name": "Dave", "value": "10"}
    new = {"id": "4", "name": "Dave", "value": "20"}
    diff.changed.append((old, new))
    sql = _render(diff)
    assert "UPDATE mytable SET" in sql
    assert "value = '20'" in sql
    assert "WHERE id = '4'" in sql


def test_changed_row_only_includes_modified_columns():
    diff = _empty_diff()
    old = {"id": "5", "name": "Eve", "value": "1"}
    new = {"id": "5", "name": "Eve", "value": "2"}
    diff.changed.append((old, new))
    sql = _render(diff)
    assert "name" not in sql.split("SET")[1].split("WHERE")[0]


def test_single_quotes_are_escaped():
    diff = _empty_diff()
    diff.added.append({"id": "6", "name": "O'Brien", "value": "0"})
    sql = _render(diff)
    assert "O''Brien" in sql
