"""CLI handler for INI output format."""
from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult
from csvdiff.render_ini import render_ini


def _render_to_stream(diff: DiffResult, columns: list, stream: io.TextIOBase) -> None:
    output = render_ini(diff, columns)
    stream.write(output)


def handle_ini_output(
    diff: DiffResult,
    columns: list,
    output_path: Optional[str] = None,
) -> None:
    """Write INI-formatted diff to *output_path* or stdout."""
    if output_path is None:
        _render_to_stream(diff, columns, sys.stdout)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        _render_to_stream(diff, columns, fh)
