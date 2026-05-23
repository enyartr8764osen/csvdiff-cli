"""Render a DiffResult as an INI-style configuration file."""
from __future__ import annotations

import io
from typing import List, Dict

from csvdiff.core import DiffResult


def _escape_value(value: str) -> str:
    """Escape special characters in INI values."""
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")


def _row_to_items(row: Dict[str, str], columns: List[str]) -> List[str]:
    lines = []
    for col in columns:
        val = _escape_value(row.get(col, ""))
        lines.append(f"{col} = {val}")
    return lines


def _write_section(
    buf: io.StringIO,
    title: str,
    rows: List[Dict[str, str]],
    columns: List[str],
) -> None:
    buf.write(f"[{title}]\n")
    if not rows:
        buf.write("; (no rows)\n")
    else:
        for idx, row in enumerate(rows):
            buf.write(f"; entry {idx}\n")
            for item in _row_to_items(row, columns):
                buf.write(f"{item}\n")
    buf.write("\n")


def render_ini(diff: DiffResult, columns: List[str]) -> str:
    """Return an INI-formatted string representing the diff."""
    if not columns:
        return ""
    buf = io.StringIO()
    _write_section(buf, "added", diff.added, columns)
    _write_section(buf, "removed", diff.removed, columns)
    changed_old = [c["old"] for c in diff.changed]
    changed_new = [c["new"] for c in diff.changed]
    _write_section(buf, "changed_old", changed_old, columns)
    _write_section(buf, "changed_new", changed_new, columns)
    return buf.getvalue()
