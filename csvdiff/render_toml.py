"""Render a DiffResult as TOML output."""
from __future__ import annotations

from typing import Dict, List

from csvdiff.core import DiffResult


def _quote(value: str) -> str:
    """Return a TOML-safe quoted string value."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _row_to_inline_table(row: Dict[str, str]) -> str:
    """Convert a row dict to a TOML inline table string."""
    pairs = ", ".join(f"{k} = {_quote(v)}" for k, v in row.items())
    return "{" + pairs + "}"


def _write_section(
    lines: List[str],
    section: str,
    rows: List[Dict[str, str]],
) -> None:
    """Append a TOML array-of-inline-tables section to lines."""
    if not rows:
        lines.append(f"{section} = []")
        return
    lines.append(f"{section} = [")
    for row in rows:
        lines.append(f"  {_row_to_inline_table(row)},")
    lines.append("]")


def render_toml(diff: DiffResult) -> str:
    """Render *diff* as a TOML document.

    The document contains three keys:
    - ``added``   – array of inline tables for added rows
    - ``removed`` – array of inline tables for removed rows
    - ``changed`` – array of tables each with ``old`` and ``new`` sub-keys
    """
    lines: List[str] = []

    _write_section(lines, "added", diff.added)
    lines.append("")
    _write_section(lines, "removed", diff.removed)

    lines.append("")
    if not diff.changed:
        lines.append("changed = []")
    else:
        lines.append("changed = [")
        for old_row, new_row in diff.changed:
            lines.append("  {")
            lines.append(f"    old = {_row_to_inline_table(old_row)},")
            lines.append(f"    new = {_row_to_inline_table(new_row)},")
            lines.append("  },")
        lines.append("]")

    return "\n".join(lines) + "\n"
