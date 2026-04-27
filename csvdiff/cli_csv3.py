"""CLI handler for the csv3 output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from csvdiff.core import DiffResult
from csvdiff.render_csv3 import render_csv3


def handle_csv3_output(
    diff: DiffResult,
    columns: List[str],
    output_path: Optional[str],
    *,
    delimiter: str = ",",
) -> None:
    """Render *diff* as csv3 and write to *output_path* or stdout."""
    content = render_csv3(diff, columns, delimiter=delimiter)

    if output_path is None:
        sys.stdout.write(content)
        return

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
