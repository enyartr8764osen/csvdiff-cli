"""CLI handler for the DOT (undirected graph) output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult
from csvdiff.render_dot import render_dot


def _render_to_stream(diff: DiffResult, stream, *, graph_name: str, include_preamble: bool) -> None:
    output = render_dot(diff, graph_name=graph_name, include_preamble=include_preamble)
    stream.write(output)


def handle_dot_output(
    diff: DiffResult,
    output_path: Optional[str],
    *,
    graph_name: str = "csvdiff",
    no_preamble: bool = False,
) -> None:
    """Write DOT output to *output_path* or stdout."""
    include_preamble = not no_preamble

    if output_path is None:
        _render_to_stream(
            diff, sys.stdout, graph_name=graph_name, include_preamble=include_preamble
        )
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, graph_name=graph_name, include_preamble=include_preamble)
