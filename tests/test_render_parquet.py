"""Tests for csvdiff.render_parquet."""
from __future__ import annotations

import pytest

from csvdiff.core import DiffResult

pyarrow = pytest.importorskip("pyarrow")
import pyarrow.parquet as pq  # noqa: E402

from csvdiff.render_parquet import render_parquet  # noqa: E402


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _read(path) -> list[dict]:
    table = pq.read_table(path)
    return table.to_pydict()


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_no_changes_produces_empty_table(tmp_path):
    dest = tmp_path / "out.parquet"
    render_parquet(_empty_diff(), dest)
    assert dest.exists()
    table = pq.read_table(dest)
    assert table.num_rows == 0
    assert "__status__" in table.schema.names


def test_added_row_appears_with_added_status(tmp_path):
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    dest = tmp_path / "out.parquet"
    render_parquet(diff, dest)
    table = pq.read_table(dest)
    statuses = table.column("__status__").to_pylist()
    assert statuses == ["added"]
    names = table.column("name").to_pylist()
    assert names == ["Alice"]


def test_removed_row_appears_with_removed_status(tmp_path):
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    dest = tmp_path / "out.parquet"
    render_parquet(diff, dest)
    table = pq.read_table(dest)
    statuses = table.column("__status__").to_pylist()
    assert statuses == ["removed"]


def test_changed_row_produces_old_and_new_rows(tmp_path):
    diff = DiffResult(
        added=[],
        removed=[],
        changed=[
            {"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}
        ],
    )
    dest = tmp_path / "out.parquet"
    render_parquet(diff, dest)
    table = pq.read_table(dest)
    assert table.num_rows == 2
    statuses = set(table.column("__status__").to_pylist())
    assert statuses == {"changed_old", "changed_new"}


def test_mixed_diff_row_count(tmp_path):
    diff = DiffResult(
        added=[{"id": "10", "val": "x"}],
        removed=[{"id": "11", "val": "y"}],
        changed=[
            {"old": {"id": "12", "val": "a"}, "new": {"id": "12", "val": "b"}}
        ],
    )
    dest = tmp_path / "out.parquet"
    render_parquet(diff, dest)
    table = pq.read_table(dest)
    # 1 added + 1 removed + 2 changed (old+new) = 4
    assert table.num_rows == 4


def test_parent_dirs_created(tmp_path):
    dest = tmp_path / "nested" / "deep" / "out.parquet"
    render_parquet(_empty_diff(), dest)
    assert dest.exists()
