"""Render a DiffResult as a Parquet file using pyarrow."""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from csvdiff.core import DiffResult

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pyarrow is required for Parquet output. "
        "Install it with: pip install pyarrow"
    ) from exc


def _rows_to_table(rows: List[Dict[str, str]], status: str) -> pa.Table:
    """Convert a list of row dicts to a PyArrow Table with a '__status__' column."""
    if not rows:
        return None
    all_keys = list(rows[0].keys())
    columns: Dict[str, List[str]] = {k: [] for k in all_keys}
    columns["__status__"] = []
    for row in rows:
        for k in all_keys:
            columns[k].append(row.get(k, ""))
        columns["__status__"].append(status)
    arrays = [pa.array(columns[k]) for k in all_keys]
    arrays.append(pa.array(columns["__status__"]))
    schema_fields = [pa.field(k, pa.string()) for k in all_keys]
    schema_fields.append(pa.field("__status__", pa.string()))
    return pa.table(
        {k: pa.array(columns[k]) for k in list(all_keys) + ["__status__"]}
    )


def render_parquet(diff: DiffResult, path: str | Path) -> None:
    """Write diff results to a Parquet file at *path*.

    Each row includes a ``__status__`` column with values
    ``'added'``, ``'removed'``, or ``'changed'``.
    Changed rows are written twice — once with status ``'changed_old'``
    and once with ``'changed_new'``.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tables: List[pa.Table] = []

    added_table = _rows_to_table(diff.added, "added")
    if added_table is not None:
        tables.append(added_table)

    removed_table = _rows_to_table(diff.removed, "removed")
    if removed_table is not None:
        tables.append(removed_table)

    old_rows = [change["old"] for change in diff.changed]
    new_rows = [change["new"] for change in diff.changed]
    old_table = _rows_to_table(old_rows, "changed_old")
    if old_table is not None:
        tables.append(old_table)
    new_table = _rows_to_table(new_rows, "changed_new")
    if new_table is not None:
        tables.append(new_table)

    if not tables:
        # Write an empty table with just the status column
        empty = pa.table({"__status__": pa.array([], type=pa.string())})
        pq.write_table(empty, path)
        return

    combined = pa.concat_tables(tables, promote_options="default")
    pq.write_table(combined, path)
