"""Render a DiffResult as a Java .properties-style file."""
from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult


def _escape_value(value: str) -> str:
    """Escape special characters in a .properties value."""
    value = value.replace("\\", "\\\\")
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    value = value.replace("=", "\\=")
    value = value.replace(":", "\\:")
    return value


def _escape_key(key: str) -> str:
    """Escape special characters in a .properties key."""
    key = key.replace("\\", "\\\\")
    key = key.replace(" ", "\\ ")
    key = key.replace("=", "\\=")
    key = key.replace(":", "\\:")
    return key


def _write_section(
    out: IO[str],
    section: str,
    rows: list[dict[str, str]],
    columns: list[str],
    index: list[int],
) -> None:
    if not rows:
        return
    out.write(f"# --- {section} ---\n")
    for row_num, row in enumerate(rows):
        prefix = f"{section.lower()}.{row_num}"
        for col in columns:
            key = _escape_key(f"{prefix}.{col}")
            val = _escape_value(row.get(col, ""))
            out.write(f"{key}={val}\n")
    out.write("\n")


def render_properties(
    diff: DiffResult,
    out: IO[str],
    *,
    columns: list[str] | None = None,
) -> None:
    """Write *diff* to *out* in .properties format."""
    cols = columns or diff.columns
    if not cols:
        return

    col_index = list(range(len(cols)))

    out.write("# csvdiff output\n\n")
    _write_section(out, "added", diff.added, cols, col_index)
    _write_section(out, "removed", diff.removed, cols, col_index)

    if diff.changed:
        out.write("# --- changed ---\n")
        for row_num, (old, new) in enumerate(diff.changed):
            prefix_old = f"changed.{row_num}.old"
            prefix_new = f"changed.{row_num}.new"
            for col in cols:
                key_old = _escape_key(f"{prefix_old}.{col}")
                key_new = _escape_key(f"{prefix_new}.{col}")
                out.write(f"{key_old}={_escape_value(old.get(col, ''))}\n")
                out.write(f"{key_new}={_escape_value(new.get(col, ''))}\n")
        out.write("\n")
