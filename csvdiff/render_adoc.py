"""Render a DiffResult as an AsciiDoc document (distinct from asciidoc table
format – this produces a full AsciiDoc document with titled sections)."""
from __future__ import annotations

from io import StringIO
from typing import List, Dict

from csvdiff.core import DiffResult


def _column_widths(rows: List[Dict[str, str]], columns: List[str]) -> Dict[str, int]:
    widths: Dict[str, int] = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(row.get(c, "")))
    return widths


def _pad(value: str, width: int) -> str:
    return value.ljust(width)


def _render_table(rows: List[Dict[str, str]], columns: List[str], out: StringIO) -> None:
    if not rows:
        out.write("_No rows._\n")
        return
    widths = _column_widths(rows, columns)
    header = " | ".join(_pad(c, widths[c]) for c in columns)
    separator = "-" * len(header)
    out.write(f"|===\n")
    out.write("| " + " | ".join(_pad(c, widths[c]) for c in columns) + "\n")
    out.write("\n")
    for row in rows:
        out.write("| " + " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns) + "\n")
    out.write("|===\n")


def render_adoc(diff: DiffResult, title: str = "CSV Diff Report") -> str:
    """Return an AsciiDoc document string representing *diff*."""
    if not diff.columns:
        return ""
    out = StringIO()
    out.write(f"= {title}\n\n")

    out.write("== Added Rows\n\n")
    _render_table(diff.added, diff.columns, out)
    out.write("\n")

    out.write("== Removed Rows\n\n")
    _render_table(diff.removed, diff.columns, out)
    out.write("\n")

    out.write("== Changed Rows\n\n")
    if not diff.changed:
        out.write("_No rows._\n")
    else:
        for old, new in diff.changed:
            out.write(".Before\n")
            _render_table([old], diff.columns, out)
            out.write(".After\n")
            _render_table([new], diff.columns, out)
            out.write("\n")
    return out.getvalue()
