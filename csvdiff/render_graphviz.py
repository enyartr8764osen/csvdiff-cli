"""Render a DiffResult as a Graphviz DOT graph."""
from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape special characters for DOT string literals."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _row_label(row: dict[str, str], columns: list[str]) -> str:
    """Build a record-style label for a DOT node."""
    parts = " | ".join(
        f"{_escape(col)}: {_escape(row.get(col, ''))}"
        for col in columns
    )
    return f"{{ {parts} }}"


def _write_nodes(
    out: IO[str],
    rows: list[dict[str, str]],
    columns: list[str],
    prefix: str,
    color: str,
    label: str,
) -> None:
    if not rows:
        return
    out.write(f'  subgraph cluster_{prefix} {{\n')
    out.write(f'    label="{label}";\n')
    out.write(f'    style=filled;\n')
    out.write(f'    fillcolor="{color}";\n')
    for idx, row in enumerate(rows):
        node_id = f"{prefix}_{idx}"
        lbl = _row_label(row, columns)
        out.write(f'    {node_id} [shape=record label="{_escape(lbl)}"];\n')
    out.write('  }\n')


def render_graphviz(
    diff: DiffResult,
    out: IO[str],
    *,
    graph_name: str = "csvdiff",
) -> None:
    """Write a DOT-language graph of *diff* to *out*."""
    columns = diff.columns
    if not columns:
        out.write(f'digraph {graph_name} {{\n}}\n')
        return

    out.write(f'digraph {graph_name} {{\n')
    out.write('  node [fontname="Helvetica"];\n')

    _write_nodes(out, diff.added, columns, "added", "#d4edda", "Added")
    _write_nodes(out, diff.removed, columns, "removed", "#f8d7da", "Removed")

    if diff.changed:
        out.write('  subgraph cluster_changed {\n')
        out.write('    label="Changed";\n')
        out.write('    style=filled;\n')
        out.write('    fillcolor="#fff3cd";\n')
        for idx, (old, new) in enumerate(diff.changed):
            old_id = f"changed_old_{idx}"
            new_id = f"changed_new_{idx}"
            old_lbl = _row_label(old, columns)
            new_lbl = _row_label(new, columns)
            out.write(f'    {old_id} [shape=record label="{_escape(old_lbl)}"];\n')
            out.write(f'    {new_id} [shape=record label="{_escape(new_lbl)}"];\n')
            out.write(f'    {old_id} -> {new_id} [label="updated"];\n')
        out.write('  }\n')

    out.write('}\n')
