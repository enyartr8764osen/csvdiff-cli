"""CLI handler for the JSON:API output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_jsonapi import render_jsonapi


def _render_to_stream(diff: DiffResult, stream: IO[str], indent: int) -> None:
    render_jsonapi(diff, stream, indent=indent)


def handle_jsonapi_output(
    diff: DiffResult,
    output: str | None,
    indent: int = 2,
) -> None:
    """Write JSON:API output to *output* path or stdout."""
    if output is None:
        _render_to_stream(diff, sys.stdout, indent)
        return

    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, indent)
