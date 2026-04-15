"""Markdown table renderer for CSV diff results."""

from typing import List
from csvdiff.core import DiffResult


def _pad(value: str, width: int) -> str:
    """Left-justify a string padded to the given width."""
    return value.ljust(width)


def _column_widths(headers: List[str], rows: List[dict]) -> dict:
    """Compute the maximum width for each column across headers and rows."""
    widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            widths[h] = max(widths[h], len(str(row.get(h, ""))))
    return widths


def _render_table(headers: List[str], rows: List[dict], status_col: bool = False) -> List[str]:
    """Render a list of dicts as a Markdown table, with an optional Status column."""
    all_headers = (["Status"] + headers) if status_col else headers
    widths = _column_widths(all_headers, rows)

    header_line = "| " + " | ".join(_pad(h, widths[h]) for h in all_headers) + " |"
    separator = "| " + " | ".join("-" * widths[h] for h in all_headers) + " |"

    lines = [header_line, separator]
    for row in rows:
        cells = [_pad(str(row.get(h, "")), widths[h]) for h in all_headers]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def render_markdown(diff: DiffResult) -> str:
    """Render a DiffResult as a Markdown document with sections for added/removed/changed rows."""
    sections: List[str] = []

    if diff.added:
        headers = list(diff.added[0].keys())
        rows = [{**row, "Status": "added"} for row in diff.added]
        sections.append("## Added Rows\n")
        sections.extend(_render_table(headers, rows, status_col=True))
        sections.append("")

    if diff.removed:
        headers = list(diff.removed[0].keys())
        rows = [{**row, "Status": "removed"} for row in diff.removed]
        sections.append("## Removed Rows\n")
        sections.extend(_render_table(headers, rows, status_col=True))
        sections.append("")

    if diff.changed:
        first_key = next(iter(diff.changed))
        old_sample = diff.changed[first_key]["old"]
        headers = list(old_sample.keys())
        rows = []
        for key, change in diff.changed.items():
            old_row = {**change["old"], "Status": "old"}
            new_row = {**change["new"], "Status": "new"}
            rows.extend([old_row, new_row])
        sections.append("## Changed Rows\n")
        sections.extend(_render_table(headers, rows, status_col=True))
        sections.append("")

    if not sections:
        return "_No differences found._\n"

    return "\n".join(sections)
