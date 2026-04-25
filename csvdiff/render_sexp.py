"""Render a DiffResult as an S-expression (Lisp-style) document."""

from __future__ import annotations

from typing import Dict, List

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape a string value for use inside a quoted S-expression atom."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _quote(value: str) -> str:
    """Wrap a value in double quotes."""
    return f'"{_escape(value)}"'


def _row_to_sexp(row: Dict[str, str], columns: List[str]) -> str:
    """Convert a row dict to an S-expression plist-style string.

    Example: (:id "1" :name "Alice")
    """
    parts = []
    for col in columns:
        parts.append(f":{col}")
        parts.append(_quote(row.get(col, "")))
    return "(" + " ".join(parts) + ")"


def _write_section(
    lines: List[str],
    label: str,
    rows: List[Dict[str, str]],
    columns: List[str],
) -> None:
    lines.append(f"({label}")
    if rows:
        for row in rows:
            lines.append("  " + _row_to_sexp(row, columns))
    lines.append(")")


def render_sexp(diff: DiffResult) -> str:
    """Return an S-expression representation of *diff*.

    The top-level form is ``(csvdiff ...)`` containing three sub-forms:
    ``(added ...)``, ``(removed ...)``, and ``(changed ...)``.
    Changed rows are represented as ``(change (old ...) (new ...))`` pairs.
    """
    columns = diff.columns
    if not columns:
        return ""

    lines: List[str] = ["(csvdiff"]

    # added
    lines.append("  (added")
    for row in diff.added:
        lines.append("    " + _row_to_sexp(row, columns))
    lines.append("  )")

    # removed
    lines.append("  (removed")
    for row in diff.removed:
        lines.append("    " + _row_to_sexp(row, columns))
    lines.append("  )")

    # changed
    lines.append("  (changed")
    for old, new in diff.changed:
        lines.append("    (change")
        lines.append("      (old " + _row_to_sexp(old, columns) + ")")
        lines.append("      (new " + _row_to_sexp(new, columns) + ")")
        lines.append("    )")
    lines.append("  )")

    lines.append(")")
    return "\n".join(lines) + "\n"
