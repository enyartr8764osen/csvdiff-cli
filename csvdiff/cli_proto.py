"""CLI handler for the proto (Protocol Buffers text) output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_proto import render_proto


def _render_to_stream(diff: DiffResult, stream: IO[str]) -> None:
    render_proto(diff, stream)


def handle_proto_output(
    diff: DiffResult,
    output_path: str | None,
) -> None:
    """Render *diff* in proto text format.

    If *output_path* is None the result is written to stdout.
    Otherwise it is written to the given file, creating parent
    directories as needed.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
