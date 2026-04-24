"""CLI handler for the csv2 output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult
from csvdiff.render_csv2 import render_csv2


def handle_csv2_output(
    diff: DiffResult,
    output_path: Optional[str],
    *,
    delimiter: str = ",",
    include_key: bool = True,
) -> None:
    """Write the csv2 render of *diff* to *output_path* or stdout.

    Parameters
    ----------
    diff:
        Diff result to serialise.
    output_path:
        Destination file path, or ``None`` to write to *stdout*.
    delimiter:
        CSV field separator forwarded to :func:`render_csv2`.
    include_key:
        Whether to include the ``_key`` helper column.
    """
    content = render_csv2(diff, delimiter=delimiter, include_key=include_key)

    if output_path is None:
        sys.stdout.write(content)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
