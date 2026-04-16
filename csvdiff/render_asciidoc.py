"""Render a DiffResult as AsciiDoc tables."""
from __future__ import annotations

from io import StringIO
from typing import List, Dict

from csvdiff.core import DiffResult


def _column_widths(rows: List[Dict[str, str]], headers: List[str]) -> Dict[str, int]:
    widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            widths[h] = max(widths[h], len(row.get(h, "")))
    return widths


def _pad(value: str, width: int) -> str:
    return value.ljust(width)


def _render_table(out: StringIO, title: str, rows: List[Dict[str, str]], headers: List[str]) -> None:
    out.write(f"=== {title}\n\n")
    if not rows:
        out.write("_No rows._\n\n")
        return
    widths = _column_widths(rows, headers)
    col_spec = ",".join(str(widths[h] + 2) for h in headers)
    out.write(f"[cols=\"{col_spec}\", options=\"header\"]\n")
    out.write("|===\n")
    header_cells = " | ".join(_pad(h, widths[h]) for h in headers)
    out.write(f"| {header_cells}\n\n")
    for row in rows:
        cells = " | ".join(_pad(row.get(h, ""), widths[h]) for h in headers)
        out.write(f"| {cells}\n")
    out.write("|===\n\n")


def render_asciidoc(diff: DiffResult) -> str:
    if not diff.columns:
        return ""
    out = StringIO()
    headers = diff.columns
    _render_table(out, "Added Rows", diff.added, headers)
    _render_table(out, "Removed Rows", diff.removed, headers)
    changed_old = [c["old"] for c in diff.changed]
    changed_new = [c["new"] for c in diff.changed]
    _render_table(out, "Changed Rows (Before)", changed_old, headers)
    _render_table(out, "Changed Rows (After)", changed_new, headers)
    return out.getvalue().rstrip() + "\n"
