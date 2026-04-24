"""Render a DiffResult as a HAML-like indented markup string."""

from __future__ import annotations

from io import StringIO
from typing import Dict, List

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape characters that are meaningful in HTML/HAML."""
    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_row(row: Dict[str, str], columns: List[str], indent: int = 4) -> str:
    """Render a single data row as HAML %tr > %td entries."""
    pad = " " * indent
    inner = " " * (indent + 2)
    lines = [f"{pad}%tr"]
    for col in columns:
        val = _escape(row.get(col, ""))
        lines.append(f"{inner}%td {val}")
    return "\n".join(lines)


def _render_section(
    buf: StringIO,
    title: str,
    rows: List[Dict[str, str]],
    columns: List[str],
) -> None:
    if not rows:
        return
    buf.write(f".section.{title.lower()}\n")
    buf.write(f"  %h2 {title}\n")
    buf.write("  %table\n")
    # header
    buf.write("    %thead\n")
    buf.write("      %tr\n")
    for col in columns:
        buf.write(f"        %th {_escape(col)}\n")
    buf.write("    %tbody\n")
    for row in rows:
        buf.write(_render_row(row, columns, indent=6))
        buf.write("\n")


def render_haml(diff: DiffResult) -> str:
    """Return a HAML-style string representing the diff sections."""
    columns = diff.columns
    if not columns:
        return ""

    buf = StringIO()
    buf.write("%div.csvdiff\n")

    _render_section(buf, "Added", diff.added, columns)
    _render_section(buf, "Removed", diff.removed, columns)

    changed_old = [entry["old"] for entry in diff.changed]
    changed_new = [entry["new"] for entry in diff.changed]
    _render_section(buf, "Changed (before)", changed_old, columns)
    _render_section(buf, "Changed (after)", changed_new, columns)

    result = buf.getvalue()
    # If nothing was written beyond the root div, signal no changes
    if result.strip() == "%div.csvdiff":
        return "%div.csvdiff\n  %p No differences found.\n"
    return result
