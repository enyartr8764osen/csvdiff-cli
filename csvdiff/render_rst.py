"""Render a DiffResult as a reStructuredText table."""

from typing import List
from csvdiff.core import DiffResult


def _pad(value: str, width: int) -> str:
    return value.ljust(width)


def _column_widths(rows: List[dict], columns: List[str]) -> List[int]:
    widths = [len(c) for c in columns]
    for row in rows:
        for i, col in enumerate(columns):
            widths[i] = max(widths[i], len(str(row.get(col, ""))))
    return widths


def _render_table(rows: List[dict], columns: List[str]) -> str:
    if not rows:
        return ""
    widths = _column_widths(rows, columns)
    sep = "  ".join("+" + "-" * (w + 2) for w in widths) + "+"
    header_cells = "  ".join(
        "| " + _pad(col, w) + " " for col, w in zip(columns, widths)
    ) + "|"
    header_sep = "  ".join("+" + "=" * (w + 2) for w in widths) + "+"

    lines = [sep, header_cells, header_sep]
    for row in rows:
        cells = "  ".join(
            "| " + _pad(str(row.get(col, "")), w) + " "
            for col, w in zip(columns, widths)
        ) + "|"
        lines.append(cells)
        lines.append(sep)
    return "\n".join(lines)


def render_rst(diff: DiffResult) -> str:
    """Return a reStructuredText string representing the diff."""
    if not diff.added and not diff.removed and not diff.changed:
        return "No differences found.\n"

    columns = diff.columns
    parts: List[str] = []

    if diff.added:
        parts.append("Added Rows\n----------")
        parts.append(_render_table(diff.added, columns))

    if diff.removed:
        parts.append("Removed Rows\n------------")
        parts.append(_render_table(diff.removed, columns))

    if diff.changed:
        old_rows = [c["old"] for c in diff.changed]
        new_rows = [c["new"] for c in diff.changed]
        parts.append("Changed Rows (old)\n------------------")
        parts.append(_render_table(old_rows, columns))
        parts.append("Changed Rows (new)\n------------------")
        parts.append(_render_table(new_rows, columns))

    return "\n\n".join(parts) + "\n"
