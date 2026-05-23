"""Render a DiffResult as a Protocol Buffers text format (.textproto)."""
from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape a string value for use inside a proto text quoted string."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _row_to_message(row: dict[str, str], indent: str = "  ") -> list[str]:
    """Convert a row dict to proto text field lines."""
    lines: list[str] = []
    for key, value in row.items():
        lines.append(f'{indent}fields {{ key: "{_escape(key)}" value: "{_escape(value)}" }}')
    return lines


def _write_section(
    out: IO[str],
    section_name: str,
    rows: list[dict[str, str]],
) -> None:
    for row in rows:
        out.write(f"{section_name} {{\n")
        for line in _row_to_message(row):
            out.write(line + "\n")
        out.write("}\n")


def _write_changed_section(
    out: IO[str],
    changes: list[tuple[dict[str, str], dict[str, str]]],
) -> None:
    for old, new in changes:
        out.write("changed {\n")
        out.write("  before {\n")
        for line in _row_to_message(old, indent="    "):
            out.write(line + "\n")
        out.write("  }\n")
        out.write("  after {\n")
        for line in _row_to_message(new, indent="    "):
            out.write(line + "\n")
        out.write("  }\n")
        out.write("}\n")


def render_proto(diff: DiffResult, out: IO[str]) -> None:
    """Write *diff* to *out* in Protocol Buffers text format."""
    columns = diff.columns
    if not columns:
        return

    _write_section(out, "added", diff.added)
    _write_section(out, "removed", diff.removed)
    _write_changed_section(out, diff.changed)
