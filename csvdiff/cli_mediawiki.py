"""CLI handler for MediaWiki output format."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csvdiff.core import DiffResult
from csvdiff.render_mediawiki import render_mediawiki


def _render_to_stream(diff: DiffResult, stream) -> None:
    output = render_mediawiki(diff)
    if output:
        stream.write(output)
        stream.write("\n")
    else:
        stream.write("No differences found.\n")


def handle_mediawiki_output(
    diff: DiffResult,
    output_path: Optional[str],
) -> None:
    """Write MediaWiki-formatted diff to *output_path* or stdout."""
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
