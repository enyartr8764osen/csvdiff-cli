"""CLI handler for the jsonpatch output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_jsonpatch import render_jsonpatch


def handle_jsonpatch_output(
    diff: DiffResult,
    output_path: str | None,
    *,
    pretty: bool = False,
) -> None:
    """Render *diff* as JSON Patch and write to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The computed diff result.
    output_path:
        Filesystem path for the output file.  ``None`` means stdout.
    pretty:
        When *True* the JSON is indented for human readability.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout, pretty=pretty)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh, pretty=pretty)


def _render_to_stream(diff: DiffResult, stream: IO[str], *, pretty: bool) -> None:
    render_jsonpatch(diff, stream, pretty=pretty)
