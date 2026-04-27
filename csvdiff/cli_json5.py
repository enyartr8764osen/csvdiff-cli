"""CLI handler for the json5 output format."""
from __future__ import annotations

import pathlib
import sys
from typing import List

from csvdiff.core import DiffResult
from csvdiff.render_json5 import render_json5


def _render_to_stream(diff: DiffResult, stream, columns: List[str] | None) -> None:
    """Write JSON5 output to *stream*."""
    text = render_json5(diff, columns=columns)
    stream.write(text)


def handle_json5_output(
    diff: DiffResult,
    output: str | None,
    columns: List[str] | None = None,
) -> None:
    """Write JSON5 diff output to *output* path or stdout.

    Parameters
    ----------
    diff:
        The diff result to render.
    output:
        Filesystem path to write to, or *None* for stdout.
    columns:
        Optional explicit column ordering.
    """
    if output is None:
        _render_to_stream(diff, sys.stdout, columns)
        return

    dest = pathlib.Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, columns)
