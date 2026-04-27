"""CLI handler for KDL output format."""
from __future__ import annotations

import io
import pathlib
import sys
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_kdl import render_kdl


def _render_to_stream(diff: DiffResult, out: IO[str]) -> None:
    render_kdl(diff, out)


def handle_kdl_output(
    diff: DiffResult,
    output_path: str | None,
) -> None:
    """Render *diff* as KDL and write to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The computed diff result.
    output_path:
        Filesystem path for the output file.  When ``None`` the KDL
        document is written to *stdout*.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return

    dest = pathlib.Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    _render_to_stream(diff, buf)
    dest.write_text(buf.getvalue(), encoding="utf-8")
