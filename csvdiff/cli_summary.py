"""CLI helper that handles --format summary output, including file writing."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, TextIO

from csvdiff.core import DiffResult
from csvdiff.render_summary import render_summary


def handle_summary_output(
    diff: DiffResult,
    output_path: Optional[str],
    *,
    color: bool = False,
) -> None:
    """Render a summary of *diff* either to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The diff result produced by :func:`csvdiff.core.diff_csv`.
    output_path:
        File path to write to, or ``None`` to write to stdout.
    color:
        Whether to emit ANSI colour codes (ignored when writing to a file).
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout, color=color)
        return

    path = Path(output_path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        # Colour codes are not useful in plain text files.
        _render_to_stream(diff, fh, color=False)


def _render_to_stream(diff: DiffResult, stream: TextIO, *, color: bool) -> None:
    render_summary(diff, stream, color=color)
