"""Render a DiffResult as a Graphviz DOT format (undirected graph)."""
from __future__ import annotations

from io import StringIO
from typing import Dict, List

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape special characters for DOT label strings."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _row_label(row: Dict[str, str], columns: List[str]) -> str:
    parts = "|".join(f"{_escape(c)}: {_escape(row.get(c, ''))}" for c in columns)
    return f"{{{parts}}}"


def _write_nodes(
    buf: StringIO,
    rows: List[Dict[str, str]],
    columns: List[str],
    prefix: str,
    shape: str,
    color: str,
) -> None:
    for i, row in enumerate(rows):
        node_id = f"{prefix}_{i}"
        label = _row_label(row, columns)
        buf.write(
            f'  {node_id} [shape={shape}, style=filled, fillcolor={color},'
            f' label="{label}"];\n'
        )


def render_dot(
    diff: DiffResult,
    *,
    graph_name: str = "csvdiff",
    include_preamble: bool = True,
) -> str:
    """Return a DOT (undirected graph) representation of *diff*."""
    columns = diff.columns
    if not columns:
        return ""

    buf = StringIO()
    if include_preamble:
        buf.write(f'graph {_escape(graph_name)} {{\n')
        buf.write('  graph [fontname="Helvetica"];\n')
        buf.write('  node [fontname="Helvetica", shape=record];\n')

    _write_nodes(buf, diff.added, columns, "added", "record", "lightgreen")
    _write_nodes(buf, diff.removed, columns, "removed", "record", "lightcoral")

    for i, (old, _new) in enumerate(diff.changed):
        old_id = f"changed_old_{i}"
        new_id = f"changed_new_{i}"
        old_label = _row_label(old, columns)
        new_label = _row_label(_new, columns)
        buf.write(
            f'  {old_id} [shape=record, style=filled, fillcolor=lightyellow,'
            f' label="{old_label}"];\n'
        )
        buf.write(
            f'  {new_id} [shape=record, style=filled, fillcolor=lightblue,'
            f' label="{new_label}"];\n'
        )
        buf.write(f"  {old_id} -- {new_id} [label=\"changed\"];\n")

    if include_preamble:
        buf.write("}\n")

    return buf.getvalue()
