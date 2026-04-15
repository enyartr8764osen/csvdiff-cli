"""Helper that wires the 'excel' output format into the CLI.

This module is imported lazily by cli.py when ``--format excel`` is requested,
keeping openpyxl an optional dependency.
"""
from __future__ import annotations

import sys
from pathlib import Path

from csvdiff.core import DiffResult


def handle_excel_output(diff: DiffResult, output: str | None) -> None:
    """Write *diff* to an Excel file.

    Parameters
    ----------
    diff:
        The computed diff result.
    output:
        Destination file path.  When *None* (i.e. the user did not supply
        ``--output``), a default name of ``csvdiff_output.xlsx`` is used and
        a notice is printed to *stderr*.
    """
    try:
        from csvdiff.render_excel import render_excel
    except ImportError:
        print(
            "error: Excel output requires openpyxl.  "
            "Install it with:  pip install openpyxl",
            file=sys.stderr,
        )
        sys.exit(1)

    path = output if output else "csvdiff_output.xlsx"

    if not output:
        print(
            f"No --output path given; writing Excel workbook to '{path}'",
            file=sys.stderr,
        )

    # Ensure the parent directory exists
    parent = Path(path).parent
    if parent and not parent.exists():
        print(
            f"error: output directory '{parent}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    render_excel(diff, path)
    print(f"Excel diff written to '{path}'", file=sys.stderr)
