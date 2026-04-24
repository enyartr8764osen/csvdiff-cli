"""Render a DiffResult as Perl POD (Plain Old Documentation) format."""

from __future__ import annotations

from typing import List, Dict

from csvdiff.core import DiffResult


def _column_widths(rows: List[Dict[str, str]], columns: List[str]) -> Dict[str, int]:
    widths: Dict[str, int] = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(row.get(col, "")))
    return widths


def _pad(value: str, width: int) -> str:
    return value.ljust(width)


def _render_table(rows: List[Dict[str, str]], columns: List[str]) -> str:
    if not rows:
        return "No rows.\n"
    widths = _column_widths(rows, columns)
    sep = "  ".join("-" * widths[col] for col in columns)
    header = "  ".join(_pad(col, widths[col]) for col in columns)
    lines = ["=begin text", "", header, sep]
    for row in rows:
        line = "  ".join(_pad(row.get(col, ""), widths[col]) for col in columns)
        lines.append(line)
    lines.extend(["", "=end text", ""])
    return "\n".join(lines) + "\n"


def render_pod(diff: DiffResult) -> str:
    """Return a POD-formatted string representing the diff."""
    if not diff.columns:
        return ""

    parts: List[str] = []
    parts.append("=pod\n")
    parts.append("=head1 CSV DIFF REPORT\n")

    parts.append("=head2 Added Rows\n")
    if diff.added:
        parts.append(_render_table(diff.added, diff.columns))
    else:
        parts.append("No added rows.\n")

    parts.append("=head2 Removed Rows\n")
    if diff.removed:
        parts.append(_render_table(diff.removed, diff.columns))
    else:
        parts.append("No removed rows.\n")

    parts.append("=head2 Changed Rows\n")
    if diff.changed:
        old_rows = [old for old, _new in diff.changed]
        new_rows = [new for _old, new in diff.changed]
        parts.append("=head3 Before\n")
        parts.append(_render_table(old_rows, diff.columns))
        parts.append("=head3 After\n")
        parts.append(_render_table(new_rows, diff.columns))
    else:
        parts.append("No changed rows.\n")

    parts.append("=cut\n")
    return "\n".join(parts)
