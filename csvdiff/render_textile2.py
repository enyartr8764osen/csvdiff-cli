"""Render a DiffResult as a Textile-formatted document with change markers."""
from __future__ import annotations

from typing import IO

from .core import DiffResult


def _column_widths(rows: list[dict[str, str]], columns: list[str]) -> dict[str, int]:
    widths: dict[str, int] = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(row.get(c, "")))
    return widths


def _pad(value: str, width: int) -> str:
    return value.ljust(width)


def _render_table(
    rows: list[dict[str, str]],
    columns: list[str],
    marker: str,
    out: IO[str],
) -> None:
    if not rows or not columns:
        return
    widths = _column_widths(rows, columns)
    header_cells = " | ".join(f"*{_pad(c, widths[c])}*" for c in columns)
    out.write(f"|_. {header_cells} |_. change |\n")
    for row in rows:
        cells = " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns)
        out.write(f"| {cells} | {marker} |\n")


def render_textile2(
    diff: DiffResult,
    out: IO[str],
    *,
    include_unchanged: bool = False,
) -> None:
    """Write a Textile table per diff section to *out*.

    Unlike the original render_textile, this variant adds a ``change``
    column so each row is self-describing.
    """
    columns = diff.columns
    if not columns:
        return

    sections = [
        ("Added", diff.added, "+added+"),
        ("Removed", diff.removed, "-removed-"),
    ]
    changed_old = [old for old, _ in diff.changed]
    changed_new = [new for _, new in diff.changed]

    has_content = diff.added or diff.removed or diff.changed
    if not has_content:
        out.write("p. No differences found.\n")
        return

    for title, rows, marker in sections:
        if not rows:
            continue
        out.write(f"h3. {title}\n\n")
        _render_table(rows, columns, marker, out)
        out.write("\n")

    if diff.changed:
        out.write("h3. Changed\n\n")
        out.write("h4. Before\n\n")
        _render_table(changed_old, columns, "~before~", out)
        out.write("\n")
        out.write("h4. After\n\n")
        _render_table(changed_new, columns, "*after*", out)
        out.write("\n")
