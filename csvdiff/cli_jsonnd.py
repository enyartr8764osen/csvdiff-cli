"""CLI handler for the ``jsonnd`` output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_jsonnd import render_jsonnd


def _render_to_stream(
    diff: DiffResult,
    stream: IO[str],
    key_columns: list[str],
    indent: int | None,
) -> None:
    render_jsonnd(diff, stream, key_columns=key_columns, indent=indent)


def handle_jsonnd_output(
    diff: DiffResult,
    output_path: str | None,
    key_columns: list[str],
    indent: int | None = None,
) -> None:
    """Write newline-delimited JSON output to *output_path* or stdout."""
    if output_path is None:
        _render_to_stream(diff, sys.stdout, key_columns, indent)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, key_columns, indent)
