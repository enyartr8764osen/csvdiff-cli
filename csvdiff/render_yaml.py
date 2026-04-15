"""Render a DiffResult as YAML."""
from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult


def _quote(value: str) -> str:
    """Return a YAML-safe scalar, quoting if necessary."""
    needs_quotes = any(c in value for c in ':#{}[]|>&*!,\'"') or value == '' or value.strip() != value
    if needs_quotes:
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _row_to_mapping(row: dict[str, str], indent: int = 6) -> list[str]:
    """Serialise a CSV row as indented YAML key-value pairs."""
    pad = ' ' * indent
    lines: list[str] = []
    for key, val in row.items():
        lines.append(f"{pad}{_quote(key)}: {_quote(val)}")
    return lines


def _write_section(label: str, rows: list[dict[str, str]], out: IO[str]) -> None:
    out.write(f"  {label}:\n")
    if not rows:
        out.write("    []\n")
        return
    for row in rows:
        out.write("    - \n")
        for line in _row_to_mapping(row, indent=6):
            out.write(line + "\n")


def render_yaml(diff: DiffResult, out: IO[str]) -> None:
    """Write *diff* to *out* as a YAML document."""
    out.write("---\n")
    out.write("csvdiff:\n")
    _write_section("added", diff.added, out)
    _write_section("removed", diff.removed, out)
    changed_rows: list[dict[str, str]] = []
    for old, new in diff.changed:
        changed_rows.append({"old": str(old), "new": str(new)})

    out.write("  changed:\n")
    if not diff.changed:
        out.write("    []\n")
        return
    for old, new in diff.changed:
        out.write("    - \n")
        out.write("      old:\n")
        for line in _row_to_mapping(old, indent=8):
            out.write(line + "\n")
        out.write("      new:\n")
        for line in _row_to_mapping(new, indent=8):
            out.write(line + "\n")
