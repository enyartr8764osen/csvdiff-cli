"""Handle --format=unified output for the csvdiff CLI."""
from __future__ import annotations

import sys
from typing import TextIO

from csvdiff.core import DiffResult
from csvdiff.render_unified import render_unified


def handle_unified_output(
    diff: DiffResult,
    *,
    out: TextIO = sys.stdout,
    context: int = 0,
    no_color: bool = False,
) -> int:
    """
    Write the unified-format diff to *out* and return an exit code.

    Returns
    -------
    0
        When there are no differences.
    1
        When at least one difference was found.
    """
    output = render_unified(diff, context=context)
    if not output:
        return 0

    if no_color:
        out.write(output)
    else:
        _write_colored(output, out)

    return 1


def _write_colored(text: str, out: TextIO) -> None:
    """Write *text* to *out*, coloring +/- lines when the terminal supports it."""
    GREEN = "\033[32m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

    for line in text.splitlines(keepends=True):
        if line.startswith("+") and not line.startswith("+++"):
            out.write(f"{GREEN}{line}{RESET}")
        elif line.startswith("-") and not line.startswith("---"):
            out.write(f"{RED}{line}{RESET}")
        elif line.startswith("@@"):
            out.write(f"{CYAN}{line}{RESET}")
        else:
            out.write(line)
