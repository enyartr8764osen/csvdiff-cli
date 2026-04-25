"""CLI handler for --format graphviz output."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_graphviz import render_graphviz


def _render_to_stream(diff: DiffResult, out: IO[str], graph_name: str) -> None:
    render_graphviz(diff, out, graph_name=graph_name)


def handle_graphviz_output(
    diff: DiffResult,
    output_path: str | None,
    *,
    graph_name: str = "csvdiff",
) -> None:
    """Write DOT output to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The computed diff result.
    output_path:
        Destination file path, or ``None`` to write to stdout.
    graph_name:
        Name embedded in the ``digraph`` declaration.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout, graph_name)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, graph_name)
