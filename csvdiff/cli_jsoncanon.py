"""CLI handler for the ``jsoncanon`` output format."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_jsoncanon import render_jsoncanon


def _render_to_stream(
    diff: DiffResult,
    stream: IO[str],
    key_columns: list[str],
    indent: int,
) -> None:
    render_jsoncanon(diff, stream, key_columns=key_columns, indent=indent)


def handle_jsoncanon_output(
    diff: DiffResult,
    output_path: str | None,
    key_columns: list[str],
    indent: int = 2,
) -> None:
    """Write canonical JSON output to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The diff result to render.
    output_path:
        Destination file path.  ``None`` means stdout.
    key_columns:
        Ordered list of column names that form the row key.
    indent:
        JSON indentation level (default 2).  Pass 0 for compact output.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout, key_columns, indent)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, key_columns, indent)
