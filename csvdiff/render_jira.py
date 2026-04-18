"""Render a DiffResult as Jira wiki markup tables."""
from __future__ import annotations
from io import StringIO
from csvdiff.core import DiffResult, has_changes


def _column_widths(rows: list[dict], columns: list[str]) -> dict[str, int]:
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))
    return widths


def _pad(value: str, width: int) -> str:
    return str(value).ljust(width)


def _render_table(rows: list[dict], columns: list[str], out: StringIO) -> None:
    if not rows:
        out.write("_(no rows)_\n")
        return
    widths = _column_widths(rows, columns)
    header_cells = " || ".join(_pad(c, widths[c]) for c in columns)
    out.write(f"|| {header_cells} ||\n")
    for row in rows:
        cells = " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns)
        out.write(f"| {cells} |\n")


def render_jira(diff: DiffResult) -> str:
    if not diff.columns:
        return ""
    out = StringIO()
    if not has_changes(diff):
        out.write("No differences found.\n")
        return out.getvalue()

    sections = [
        ("Added Rows", diff.added),
        ("Removed Rows", diff.removed),
    ]
    for title, rows in sections:
        out.write(f"h3. {title}\n")
        _render_table(rows, diff.columns, out)
        out.write("\n")

    if diff.changed:
        out.write("h3. Changed Rows\n")
        out.write("h4. Before\n")
        _render_table([c["old"] for c in diff.changed], diff.columns, out)
        out.write("h4. After\n")
        _render_table([c["new"] for c in diff.changed], diff.columns, out)
        out.write("\n")

    return out.getvalue()
