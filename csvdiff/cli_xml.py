"""Handle XML output for the csvdiff CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult
from csvdiff.render_xml import render_xml


def handle_xml_output(
    diff: DiffResult,
    output_path: Optional[str],
) -> None:
    """Render *diff* as XML, writing to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The computed diff result.
    output_path:
        Filesystem path for the output file, or ``None`` to write to stdout.
    """
    if output_path is None:
        render_xml(diff, sys.stdout)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        render_xml(diff, fh)
