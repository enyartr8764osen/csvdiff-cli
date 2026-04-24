"""CLI helper for AsciiDoc document output."""
from __future__ import annotations

import sys
from pathlib import Path

from csvdiff.core import DiffResult
from csvdiff.render_adoc import render_adoc


def _render_to_stream(diff: DiffResult, stream, title: str) -> None:
    output = render_adoc(diff, title=title)
    stream.write(output)


def handle_adoc_output(
    diff: DiffResult,
    output_path: str | None,
    title: str = "CSV Diff Report",
) -> None:
    """Write AsciiDoc output to *output_path* or stdout."""
    if output_path is None:
        _render_to_stream(diff, sys.stdout, title)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, title)
