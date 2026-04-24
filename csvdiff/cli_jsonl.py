"""CLI helper for the JSON Lines output format."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from csvdiff.core import DiffResult
from csvdiff.render_jsonl import render_jsonl


def handle_jsonl_output(
    diff: DiffResult,
    key_cols: List[str],
    output_path: str | None,
) -> None:
    """Write the JSON Lines diff to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The computed :class:`~csvdiff.core.DiffResult`.
    key_cols:
        Column names that form the primary key.
    output_path:
        Filesystem path for the output file, or ``None`` to write to
        standard output.
    """
    if output_path is None:
        render_jsonl(diff, key_cols, stream=sys.stdout)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        render_jsonl(diff, key_cols, stream=fh)
