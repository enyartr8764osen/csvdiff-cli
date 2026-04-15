"""CLI helper for the YAML output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

from csvdiff.core import DiffResult
from csvdiff.render_yaml import render_yaml


def _render_to_stream(diff: DiffResult, stream: IO[str]) -> None:
    render_yaml(diff, stream)


def handle_yaml_output(diff: DiffResult, output_path: str | None) -> None:
    """Write YAML-formatted diff to *output_path* or stdout."""
    if output_path is None:
        _render_to_stream(diff, sys.stdout)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        _render_to_stream(diff, fh)
