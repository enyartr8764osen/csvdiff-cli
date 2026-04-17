"""CLI handler for BBCode output format."""
from __future__ import annotations
import sys
from pathlib import Path
from .core import DiffResult
from .render_bbcode import render_bbcode


def _render_to_stream(diff: DiffResult, stream) -> None:
    output = render_bbcode(diff)
    if output:
        stream.write(output)
        stream.write("\n")


def handle_bbcode_output(diff: DiffResult, output_path: str | None) -> None:
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
