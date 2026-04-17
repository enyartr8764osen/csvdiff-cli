"""Render diff as Confluence wiki markup tables."""
from __future__ import annotations
from io import StringIO
from csvdiff.core import DiffResult


def _column_widths(rows: list[dict], columns: list[str]) -> dict[str, int]:
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))
    return widths


def _pad(value: str, width: int) -> str:
    return str(value).ljust(width)


def _render_table(title: str, rows: list[dict], columns: list[str], out: StringIO) -> None:
    if not rows:
        out.write(f"h3. {title}\n\nNo rows.\n\n")
        return
    widths = _column_widths(rows, columns)
    out.write(f"h3. {title}\n\n")
    header = " || ".join(_pad(c, widths[c]) for c in columns)
    out.write(f"|| {header} ||\n")
    for row in rows:
        cells = " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns)
        out.write(f"| {cells} |\n")
    out.write("\n")


def render_confluence(diff: DiffResult) -> str:
    if not diff.columns:
        return ""
    out = StringIO()
    _render_table("Added Rows", diff.added, diff.columns, out)
    _render_table("Removed Rows", diff.removed, diff.columns, out)
    changed_old = [c["old"] for c in diff.changed]
    changed_new = [c["new"] for c in diff.changed]
    _render_table("Changed Rows (Before)", changed_old, diff.columns, out)
    _render_table("Changed Rows (After)", changed_new, diff.columns, out)
    return out.getvalue().rstrip("\n")
