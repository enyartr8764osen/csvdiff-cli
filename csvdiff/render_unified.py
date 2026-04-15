"""Render diff output in a unified-diff-like text format."""
from __future__ import annotations

from typing import List

from csvdiff.core import DiffResult


def _format_row(row: dict, columns: List[str], prefix: str) -> str:
    """Format a single CSV row with a +/- prefix."""
    values = ",".join(str(row.get(c, "")) for c in columns)
    return f"{prefix}{values}"


def render_unified(diff: DiffResult, *, context: int = 0) -> str:
    """
    Render *diff* as a unified-diff-inspired plain-text string.

    Each added row is prefixed with ``+``, each removed row with ``-``,
    and changed rows show the old line (``-``) followed by the new line
    (``+``).  A header line lists the column names.

    Parameters
    ----------
    diff:
        The :class:`~csvdiff.core.DiffResult` to render.
    context:
        Reserved for future use (number of unchanged context rows).
        Currently unused but accepted for API compatibility.
    """
    if not diff.columns:
        return ""

    lines: List[str] = []
    header = ",".join(diff.columns)
    has_output = bool(diff.added or diff.removed or diff.changed)

    if not has_output:
        return ""

    lines.append(f"--- a")
    lines.append(f"+++ b")
    lines.append(f"@@ columns: {header} @@")

    for row in diff.removed:
        lines.append(_format_row(row, diff.columns, "-"))

    for old_row, new_row in diff.changed:
        lines.append(_format_row(old_row, diff.columns, "-"))
        lines.append(_format_row(new_row, diff.columns, "+"))

    for row in diff.added:
        lines.append(_format_row(row, diff.columns, "+"))

    return "\n".join(lines) + "\n"
