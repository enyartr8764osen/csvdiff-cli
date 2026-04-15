"""Render a compact summary of diff results."""
from __future__ import annotations

from typing import TextIO

from csvdiff.core import DiffResult, has_changes


def render_summary(diff: DiffResult, out: TextIO, *, color: bool = False) -> None:
    """Write a compact human-readable summary of *diff* to *out*.

    Example output::

        Summary: 2 added, 1 removed, 3 changed (6 rows examined)

    When *color* is True ANSI escape codes are used to highlight counts.
    """
    added = len(diff["added"])
    removed = len(diff["removed"])
    changed = len(diff["changed"])
    total = added + removed + changed

    if not has_changes(diff):
        _write(out, "No differences found.", color and "\033[32m")
        out.write("\n")
        return

    parts = []
    if added:
        parts.append(_fmt(added, "added", color and "\033[32m"))
    if removed:
        parts.append(_fmt(removed, "removed", color and "\033[31m"))
    if changed:
        parts.append(_fmt(changed, "changed", color and "\033[33m"))

    rows_note = f"({total} row{'s' if total != 1 else ''} affected)"
    out.write("Summary: " + ", ".join(parts) + " " + rows_note + "\n")


def _fmt(count: int, label: str, ansi: str) -> str:
    text = f"{count} {label}"
    if ansi:
        return f"{ansi}{text}\033[0m"
    return text


def _write(out: TextIO, text: str, ansi: str) -> None:
    if ansi:
        out.write(f"{ansi}{text}\033[0m")
    else:
        out.write(text)
