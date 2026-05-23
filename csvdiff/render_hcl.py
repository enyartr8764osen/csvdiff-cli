"""Render a DiffResult as HCL (HashiCorp Configuration Language)."""

from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape a string value for use inside HCL double-quoted strings."""
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    return value


def _row_to_block(row: dict[str, str], index: int, stream: IO[str]) -> None:
    """Write a single row as an HCL 'row' block."""
    stream.write(f'  row "{index}" {{\n')
    for key, value in row.items():
        stream.write(f'    {key} = "{_escape(value)}"\n')
    stream.write("  }\n")


def _write_section(
    label: str,
    rows: list[dict[str, str]],
    stream: IO[str],
) -> None:
    stream.write(f'{label} {{\n')
    if not rows:
        stream.write("  # no rows\n")
    else:
        for i, row in enumerate(rows):
            _row_to_block(row, i, stream)
    stream.write("}\n")


def render_hcl(diff: DiffResult, stream: IO[str]) -> None:
    """Write *diff* to *stream* in HCL format.

    The output contains three top-level blocks: ``added``, ``removed``, and
    ``changed``.  Each block contains zero or more ``row`` sub-blocks whose
    label is the row index (0-based).  Changed rows include both ``old`` and
    ``new`` nested blocks.
    """
    if not diff.columns:
        return

    _write_section("added", diff.added, stream)
    stream.write("\n")
    _write_section("removed", diff.removed, stream)
    stream.write("\n")

    stream.write("changed {\n")
    if not diff.changed:
        stream.write("  # no rows\n")
    else:
        for i, (old, new) in enumerate(diff.changed):
            stream.write(f'  row "{i}" {{\n')
            stream.write("    old {\n")
            for key, value in old.items():
                stream.write(f'      {key} = "{_escape(value)}"\n')
            stream.write("    }\n")
            stream.write("    new {\n")
            for key, value in new.items():
                stream.write(f'      {key} = "{_escape(value)}"\n')
            stream.write("    }\n")
            stream.write("  }\n")
    stream.write("}\n")
