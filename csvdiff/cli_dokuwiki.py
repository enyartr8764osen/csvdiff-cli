"""CLI handler for DokuWiki output format."""
from __future__ import annotations
import sys
from pathlib import Path
from csvdiff.core import DiffResult
from csvdiff.render_dokuwiki import render_dokuwiki


def _render_to_stream(diff: DiffResult, stream) -> None:
    output = render_dokuwiki(diff)
    stream.write(output)


def handle_dokuwiki_output(diff: DiffResult, output_path: str | None) -> None:
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _render_to_stream(diff, fh)
