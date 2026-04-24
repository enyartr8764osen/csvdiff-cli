"""CLI handler for s-expression output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

from csvdiff.core import DiffResult
from csvdiff.render_s3v import render_s3v


def _render_to_stream(diff: DiffResult, stream: TextIO) -> None:
    render_s3v(diff, stream)


def handle_s3v_output(diff: DiffResult, output: str | None) -> None:
    """Write s-expression diff to *output* path or stdout."""
    if output is None:
        _render_to_stream(diff, sys.stdout)
        return

    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
