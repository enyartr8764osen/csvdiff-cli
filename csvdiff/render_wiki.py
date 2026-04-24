"""Render a DiffResult as Google Code / Trac-style wiki table markup."""
from __future__ import annotations

from io import StringIO
from typing import List

from csvdiff.core import DiffResult


def _column_widths(rows: List[dict], columns: List[str]) -> List[int]:
    widths = [len(c) for c in columns]
    for row in rows:
        for i, col in enumerate(columns):
            widths[i] = max(widths[i], len(str(row.get(col, ""))))
    return widths


def _pad(text: str, width: int) -> str:
    return str(text).ljust(width)


def _render_table(
    buf: StringIO,
    title: str,
    rows: List[dict],
    columns: List[str],
) -> None:
    if not columns:
        return
    buf.write(f"== {title} ==\n")
    if not rows:
        buf.write("(no rows)\n\n")
        return
    widths = _column_widths(rows, columns)
    header_cells = " || ".join(_pad(c, widths[i]) for i, c in enumerate(columns))
    buf.write(f"|| {header_cells} ||\n")
    for row in rows:
        cells = " || ".join(
            _pad(row.get(c, ""), widths[i]) for i, c in enumerate(columns)
        )
        buf.write(f"|| {cells} ||\n")
    buf.write("\n")


def render_wiki(diff: DiffResult) -> str:
    """Return a wiki-markup string representing *diff*."""
    if not diff.columns:
        return ""
    buf = StringIO()
    added_rows = [r["new"] for r in diff.changed] + diff.added
    removed_rows = [r["old"] for r in diff.changed] + diff.removed
    _render_table(buf, "Added Rows", diff.added, diff.columns)
    _render_table(buf, "Removed Rows", diff.removed, diff.columns)
    _render_table(
        buf,
        "Changed Rows (before)",
        [r["old"] for r in diff.changed],
        diff.columns,
    )
    _render_table(
        buf,
        "Changed Rows (after)",
        [r["new"] for r in diff.changed],
        diff.columns,
    )
    return buf.getvalue()
