"""CLI handler for OpenDocument Spreadsheet (.ods) output."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult


def handle_opendoc_output(
    diff: DiffResult,
    output_path: Optional[str],
) -> None:
    """Render *diff* as an ODS file.

    *output_path* must be provided; ODS is a binary format and cannot be
    written to stdout.
    """
    try:
        from csvdiff.render_opendoc import render_opendoc
    except ImportError as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not output_path:
        print(
            "Error: --output is required for ODS format (binary output).",
            file=sys.stderr,
        )
        sys.exit(1)

    dest = Path(output_path)
    render_opendoc(diff, dest)
    print(f"ODS diff written to {dest}", file=sys.stderr)
