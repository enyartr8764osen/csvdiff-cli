"""Render a DiffResult as a Rich Text Format (RTF) document."""

from __future__ import annotations

from typing import List

from csvdiff.core import DiffResult


def _escape(text: str) -> str:
    """Escape special RTF characters."""
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    return text


def _row_to_cells(row: dict, columns: List[str], cell_width: int = 1800) -> str:
    """Render a single table row as RTF table cells."""
    cells = ""
    for col in columns:
        value = _escape(str(row.get(col, "")))
        cells += f"\\intbl {value}\\cell "
    return cells


def _render_section(title: str, rows: List[dict], columns: List[str]) -> str:
    """Render a titled section with a table of rows."""
    if not rows:
        return ""

    lines: List[str] = []
    lines.append(f"{{\\b {_escape(title)}}}\\par")

    # Header row
    header_cells = ""
    for col in columns:
        header_cells += f"{{\\b {_escape(col)}}}\\cell "
    lines.append(f"\\trowd {header_cells}\\row")

    for row in rows:
        lines.append(f"\\trowd {_row_to_cells(row, columns)}\\row")

    lines.append("\\par")
    return "\n".join(lines)


def render_rtf(diff: DiffResult) -> str:
    """Return an RTF document string representing the diff."""
    columns = diff.columns

    if not columns:
        return ""

    body_parts: List[str] = []

    added_section = _render_section("Added Rows", diff.added, columns)
    if added_section:
        body_parts.append(added_section)

    removed_section = _render_section("Removed Rows", diff.removed, columns)
    if removed_section:
        body_parts.append(removed_section)

    changed_section_parts: List[str] = []
    if diff.changed:
        changed_section_parts.append("{\\b Changed Rows}\\par")
        for old, new in diff.changed:
            changed_section_parts.append("{\\i Before:}\\par")
            changed_section_parts.append(f"\\trowd {_row_to_cells(old, columns)}\\row")
            changed_section_parts.append("{\\i After:}\\par")
            changed_section_parts.append(f"\\trowd {_row_to_cells(new, columns)}\\row")
        changed_section_parts.append("\\par")
        body_parts.append("\n".join(changed_section_parts))

    if not body_parts:
        body_parts.append("{\\i No differences found.}\\par")

    body = "\n".join(body_parts)
    return (
        "{\\rtf1\\ansi\\deff0\n"
        "{\\fonttbl{\\f0 Courier New;}}\n"
        "\\f0\\fs20\n"
        f"{body}\n"
        "}"
    )
