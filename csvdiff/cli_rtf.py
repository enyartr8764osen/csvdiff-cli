"""CLI handler for RTF output format."""

from __future__ import annotations

import pathlib
import sys

from csvdiff.core import DiffResult
from csvdiff.render_rtf import render_rtf


def _render_to_stream(diff: DiffResult, stream) -> None:
    """Write RTF output to *stream*."""
    content = render_rtf(diff)
    stream.write(content)


def handle_rtf_output(diff: DiffResult, output_path: str | None) -> None:
    """Write RTF diff output to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The computed :class:`~csvdiff.core.DiffResult`.
    output_path:
        Filesystem path to write the ``.rtf`` file, or ``None`` to write
        to *stdout*.
    """
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return

    dest = pathlib.Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
