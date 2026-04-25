"""CLI integration for the textile2 renderer."""
from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import IO

from .core import DiffResult
from .render_textile2 import render_textile2


def _render_to_stream(diff: DiffResult, out: IO[str], **kwargs: object) -> None:
    render_textile2(diff, out, **kwargs)  # type: ignore[arg-type]


def handle_textile2_output(
    diff: DiffResult,
    output_path: str | None,
    *,
    include_unchanged: bool = False,
) -> None:
    """Write textile2-formatted diff to *output_path* or stdout."""
    kwargs = {"include_unchanged": include_unchanged}

    if output_path is None:
        _render_to_stream(diff, sys.stdout, **kwargs)
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    _render_to_stream(diff, buf, **kwargs)
    path.write_text(buf.getvalue(), encoding="utf-8")
