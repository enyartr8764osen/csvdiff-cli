"""Render a DiffResult as a MediaWiki markup table."""

from __future__ import annotations

from io import StringIO
from typing import List, Dict

from csvdiff.core import DiffResult, has_changes


def _pad(text: str, width: int) -> str:
    return text.ljust(width)


def _column_widths(rows: List[Dict[str, str]], columns: List[str]) -> Dict[str, int]:
    widths: Dict[str, int] = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(row.get(col, "")))
    return widths


def _render_table(
    buf: StringIO,
    title: str,
    rows: List[Dict[str, str]],
    columns: List[str],
) -> None:
    if not rows:
        return
    widths = _column_widths(rows, columns)
    buf.write(f"== {title} ==\n")
    buf.write("{| class=\"wikitable\"\n")
    buf.write("|-\n")
    header_cells = " || ".join(_pad(col, widths[col]) for col in columns)
    buf.write(f"! {header_cells}\n")
    for row in rows:
        buf.write("|-\n")
        cells = " || ".join(_pad(row.get(col, ""), widths[col]) for col in columns)
        buf.write(f"| {cells}\n")
    buf.write("|}")  
    buf.write("\n\n")


def render_mediawiki(diff: DiffResult) -> str:
    """Return MediaWiki markup representing *diff*.

    Returns an empty string when there are no changes.
    """
    if not has_changes(diff):
        return ""

    buf = StringIO()
    columns = diff.columns

    _render_table(buf, "Added Rows", diff.added, columns)
    _render_table(buf, "Removed Rows", diff.removed, columns)

    changed_old = [change["old"] for change in diff.changed]
    changed_new = [change["new"] for change in diff.changed]
    _render_table(buf, "Changed Rows (before)", changed_old, columns)
    _render_table(buf, "Changed Rows (after)", changed_new, columns)

    return buf.getvalue().rstrip("\n")
