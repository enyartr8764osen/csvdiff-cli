"""Render a DiffResult as JSON5 output.

JSON5 is a superset of JSON that allows comments, trailing commas,
and unquoted keys, making it more human-readable.
"""
from __future__ import annotations

import io
from typing import Dict, List, Tuple

from csvdiff.core import DiffResult


def _quote(value: str) -> str:
    """Return a JSON5-compatible double-quoted string."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _row_to_obj(row: Dict[str, str], indent: int = 4) -> str:
    """Render a single row dict as a JSON5 object literal."""
    pad = " " * indent
    lines = ["  {"]
    items = list(row.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i < len(items) - 1 else ","  # trailing comma allowed in JSON5
        lines.append(f"{pad}{k}: {_quote(v)}{comma}")
    lines.append("  }")
    return "\n".join(lines)


def _write_section(
    buf: io.StringIO,
    label: str,
    rows: List[Dict[str, str]],
    last: bool,
) -> None:
    section_comma = "" if last else ","
    buf.write(f"  // {label} rows\n")
    buf.write(f"  {label}: [\n")
    for i, row in enumerate(rows):
        row_comma = "," if i < len(rows) - 1 else ","  # trailing comma
        buf.write(_row_to_obj(row))
        buf.write(row_comma + "\n")
    buf.write(f"  ]{section_comma}\n")


def render_json5(
    diff: DiffResult,
    *,
    columns: List[str] | None = None,
) -> str:
    """Return a JSON5 string representing the diff.

    Parameters
    ----------
    diff:
        The diff result to render.
    columns:
        Optional explicit column list; if *None* the columns are inferred
        from the diff data.
    """
    if columns is None:
        all_rows: List[Dict[str, str]] = (
            list(diff.added) + list(diff.removed)
            + [r for _, r in diff.changed]
        )
        columns = list(all_rows[0].keys()) if all_rows else []

    if not columns:
        return "{\n  added: [],\n  removed: [],\n  changed: [],\n}\n"

    changed_rows: List[Dict[str, str]] = [new for _, new in diff.changed]

    buf = io.StringIO()
    buf.write("{\n")
    _write_section(buf, "added", list(diff.added), last=False)
    _write_section(buf, "removed", list(diff.removed), last=False)
    _write_section(buf, "changed", changed_rows, last=True)
    buf.write("}\n")
    return buf.getvalue()
