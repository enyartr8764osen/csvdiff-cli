"""Render a DiffResult as Textile markup."""
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


def _render_table(buf: StringIO, rows: list[dict], columns: list[str]) -> None:
    if not rows:
        return
    widths = _column_widths(rows, columns)
    header = "|".join(f"_.{_pad(c, widths[c])}" for c in columns)
    buf.write(f"|{header}|\n")
    for row in rows:
        line = "|".join(_pad(row.get(c, ""), widths[c]) for c in columns)
        buf.write(f"|{line}|\n")


def render_textile(diff: DiffResult) -> str:
    if not has_changes(diff):
        return ""
    buf = StringIO()
    columns = diff.columns

    if diff.added:
        buf.write("h2. Added\n\n")
        _render_table(buf, diff.added, columns)
        buf.write("\n")

    if diff.removed:
        buf.write("h2. Removed\n\n")
        _render_table(buf, diff.removed, columns)
        buf.write("\n")

    if diff.changed:
        buf.write("h2. Changed\n\n")
        for old, new in diff.changed:
            buf.write("*Before:*\n\n")
            _render_table(buf, [old], columns)
            buf.write("\n*After:*\n\n")
            _render_table(buf, [new], columns)
            buf.write("\n")

    return buf.getvalue()
