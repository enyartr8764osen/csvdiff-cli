"""CLI handler for plist output format."""
from __future__ import annotations

import sys
from pathlib import Path

from csvdiff.core import DiffResult
from csvdiff.render_plist import render_plist


def handle_plist_output(diff: DiffResult, output_path: str | None) -> None:
    """Render *diff* as a plist document and write to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The diff result to render.
    output_path:
        Filesystem path for the output file.  When ``None`` the rendered text
        is written to *stdout*.
    """
    text = render_plist(diff)

    if output_path is None:
        sys.stdout.write(text)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
