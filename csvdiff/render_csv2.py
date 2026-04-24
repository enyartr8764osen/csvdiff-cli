"""Render a DiffResult as a CSV with a 'status' column prepended."""
from __future__ import annotations

import csv
import io
from typing import List

from csvdiff.core import DiffResult


def render_csv2(
    diff: DiffResult,
    *,
    delimiter: str = ",",
    include_key: bool = True,
) -> str:
    """Return a CSV string with a leading *status* column.

    Each row carries one of three status values:
      - ``added``   – row present only in the new file
      - ``removed`` – row present only in the old file
      - ``changed`` – row whose non-key values differ (old values used)
      - ``changed_new`` – the new version of a changed row

    Parameters
    ----------
    diff:
        The :class:`~csvdiff.core.DiffResult` to render.
    delimiter:
        Field separator (default ``,``).
    include_key:
        When *True* (default) the key tuple is written as the second
        column after *status*.
    """
    if not diff.columns:
        return ""

    buf = io.StringIO()
    extra_cols: List[str] = ["status"]
    if include_key:
        extra_cols.append("_key")
    header = extra_cols + diff.columns

    writer = csv.writer(buf, delimiter=delimiter, lineterminator="\n")
    writer.writerow(header)

    def _write(status: str, row: dict) -> None:
        key_str = "|".join(str(v) for v in diff.key_columns) if include_key else None
        # resolve actual key values from the row
        key_val = "|".join(str(row.get(k, "")) for k in diff.key_columns)
        extras = [status, key_val] if include_key else [status]
        writer.writerow(extras + [row.get(c, "") for c in diff.columns])

    for key, row in diff.added.items():
        _write("added", row)

    for key, row in diff.removed.items():
        _write("removed", row)

    for key, (old_row, new_row) in diff.changed.items():
        _write("changed", old_row)
        _write("changed_new", new_row)

    return buf.getvalue()
