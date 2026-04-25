"""Render a DiffResult as a Mustache-style template output (plain text tables).

Produces a human-readable diff using a simple mustache-inspired section
format: {{#added}}, {{#removed}}, {{#changed}}.
"""

from __future__ import annotations

from io import StringIO
from typing import List

from csvdiff.core import DiffResult


def _column_widths(headers: List[str], rows: List[dict]) -> List[int]:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, h in enumerate(headers):
            widths[i] = max(widths[i], len(str(row.get(h, ""))))
    return widths


def _pad(value: str, width: int) -> str:
    return str(value).ljust(width)


def _render_table(out: StringIO, headers: List[str], rows: List[dict]) -> None:
    if not rows:
        out.write("  (no rows)\n")
        return
    widths = _column_widths(headers, rows)
    header_line = "  | " + " | ".join(_pad(h, widths[i]) for i, h in enumerate(headers)) + " |"
    separator = "  |" + "|".join("-" * (w + 2) for w in widths) + "|"
    out.write(header_line + "\n")
    out.write(separator + "\n")
    for row in rows:
        cells = " | ".join(_pad(row.get(h, ""), widths[i]) for i, h in enumerate(headers))
        out.write("  | " + cells + " |\n")


def render_mustache(diff: DiffResult) -> str:
    """Return a Mustache-section formatted string representing *diff*."""
    if not diff.columns:
        return ""

    out = StringIO()
    headers = diff.columns

    out.write("{{#added}}\n")
    _render_table(out, headers, diff.added)
    out.write("{{/added}}\n\n")

    out.write("{{#removed}}\n")
    _render_table(out, headers, diff.removed)
    out.write("{{/removed}}\n\n")

    out.write("{{#changed}}\n")
    changed_rows: List[dict] = []
    for old, new in diff.changed:
        changed_rows.append({h: f"{old.get(h, '')} -> {new.get(h, '')}" for h in headers})
    _render_table(out, headers, changed_rows)
    out.write("{{/changed}}\n")

    return out.getvalue()
