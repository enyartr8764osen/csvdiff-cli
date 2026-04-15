"""Render a DiffResult as SQL INSERT/DELETE/UPDATE statements."""
from __future__ import annotations

from typing import IO, List

from csvdiff.core import DiffResult


def _quote(value: str) -> str:
    """Wrap a value in single quotes, escaping internal single quotes."""
    return "'" + value.replace("'", "''") + "'"


def _col_list(columns: List[str]) -> str:
    return ", ".join(columns)


def _val_list(row: dict, columns: List[str]) -> str:
    return ", ".join(_quote(row[c]) for c in columns)


def _where_clause(row: dict, key_columns: List[str]) -> str:
    parts = [f"{k} = {_quote(row[k])}" for k in key_columns]
    return " AND ".join(parts)


def render_sql(
    diff: DiffResult,
    table: str,
    out: IO[str],
    key_columns: List[str] | None = None,
) -> None:
    """Write SQL statements representing the diff to *out*.

    - Added rows  -> INSERT INTO ...
    - Removed rows -> DELETE FROM ...
    - Changed rows -> UPDATE ... SET ...
    """
    if not diff.columns:
        return

    keys = key_columns or diff.columns[:1]

    for row in diff.added:
        cols = _col_list(diff.columns)
        vals = _val_list(row, diff.columns)
        out.write(f"INSERT INTO {table} ({cols}) VALUES ({vals});\n")

    for row in diff.removed:
        where = _where_clause(row, keys)
        out.write(f"DELETE FROM {table} WHERE {where};\n")

    for old, new in diff.changed:
        non_key = [c for c in diff.columns if c not in keys]
        if not non_key:
            continue
        set_parts = ", ".join(
            f"{c} = {_quote(new[c])}" for c in non_key if old[c] != new[c]
        )
        if not set_parts:
            continue
        where = _where_clause(old, keys)
        out.write(f"UPDATE {table} SET {set_parts} WHERE {where};\n")
