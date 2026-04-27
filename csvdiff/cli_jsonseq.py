"""CLI handler for the JSON Text Sequence (jsonseq) output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_jsonseq import render_jsonseq


def _render_to_stream(diff: DiffResult, stream: IO[str], indent: int | None) -> None:
    render_jsonseq(diff, stream, indent=indent)


def handle_jsonseq_output(
    diff: DiffResult,
    output_path: str | None,
    *,
    indent: int | None = None,
) -> None:
    """Write *diff* as JSON Text Sequences to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The diff result to render.
    output_path:
        Destination file path, or ``None`` to write to stdout.
    indent:
        Optional JSON indentation level passed through to ``json.dumps``.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout, indent)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, indent)
