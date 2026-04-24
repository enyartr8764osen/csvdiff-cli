"""Render diff as S-expression (s-expr) structured text."""
from __future__ import annotations

from typing import TextIO

from csvdiff.core import DiffResult


def _quote(value: str) -> str:
    """Quote a string value for use in an s-expression."""
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def _row_to_sexp(row: dict[str, str]) -> str:
    """Convert a row dict to an s-expression association list."""
    pairs = " ".join(
        f"({_quote(k)} . {_quote(v)})" for k, v in row.items()
    )
    return f"({pairs})"


def _write_section(out: TextIO, tag: str, rows: list[dict[str, str]]) -> None:
    out.write(f"  ({tag}\n")
    if rows:
        for row in rows:
            out.write(f"    {_row_to_sexp(row)}\n")
    else:
        out.write("    ()\n")
    out.write("  )\n")


def render_s3v(diff: DiffResult, out: TextIO) -> None:
    """Render *diff* as an s-expression document written to *out*."""
    if not diff.columns:
        return

    out.write("(csvdiff\n")
    _write_section(out, "added", diff.added)
    _write_section(out, "removed", diff.removed)
    changed_rows = [new for _old, new in diff.changed]
    _write_section(out, "changed", changed_rows)
    out.write(")\n")
