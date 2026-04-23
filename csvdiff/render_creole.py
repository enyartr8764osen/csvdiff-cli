"""Render a DiffResult as Creole wiki markup."""
from __future__ import annotations

from typing import List

from csvdiff.core import DiffResult


def _column_widths(rows: List[dict], columns: List[str]) -> List[int]:
    widths = [len(c) for c in columns]
    for row in rows:
        for i, col in enumerate(columns):
            widths[i] = max(widths[i], len(str(row.get(col, ""))))
    return widths


def _pad(value: str, width: int) -> str:
    return str(value).ljust(width)


def _render_table(title: str, rows: List[dict], columns: List[str]) -> str:
    if not columns:
        return ""
    lines: List[str] = []
    lines.append(f"== {title} ==")
    if not rows:
        lines.append("(no rows)")
        return "\n".join(lines)

    widths = _column_widths(rows, columns)

    header_cells = " | ".join(
        f"**{_pad(col, widths[i])}**" for i, col in enumerate(columns)
    )
    lines.append(f"|= {header_cells} |")

    for row in rows:
        cells = " | ".join(
            _pad(str(row.get(col, "")), widths[i])
            for i, col in enumerate(columns)
        )
        lines.append(f"| {cells} |")

    return "\n".join(lines)


def render_creole(diff: DiffResult) -> str:
    """Return a Creole wiki markup string representing *diff*."""
    if not diff.columns:
        return ""

    sections: List[str] = []

    added_block = _render_table("Added Rows", diff.added, diff.columns)
    if added_block:
        sections.append(added_block)

    removed_block = _render_table("Removed Rows", diff.removed, diff.columns)
    if removed_block:
        sections.append(removed_block)

    if diff.changed:
        old_rows = [old for old, _new in diff.changed]
        new_rows = [new for _old, new in diff.changed]
        sections.append(_render_table("Changed Rows (before)", old_rows, diff.columns))
        sections.append(_render_table("Changed Rows (after)", new_rows, diff.columns))

    return "\n\n".join(sections)
