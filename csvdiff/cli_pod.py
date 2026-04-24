"""CLI handler for POD output format."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult
from csvdiff.render_pod import render_pod


def _render_to_stream(diff: DiffResult, stream) -> None:
    output = render_pod(diff)
    stream.write(output)


def handle_pod_output(
    diff: DiffResult,
    output_path: Optional[str] = None,
) -> None:
    """Write POD-formatted diff to *output_path* or stdout."""
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
