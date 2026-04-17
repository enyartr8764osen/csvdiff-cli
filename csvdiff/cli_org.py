"""CLI handler for Org-mode output format."""
from pathlib import Path
import sys
from .core import DiffResult
from .render_org import render_org


def _render_to_stream(diff: DiffResult, stream, no_ansi: bool = False):
    stream.write(render_org(diff))


def handle_org_output(diff: DiffResult, output_path: str | None, **kwargs):
    text = render_org(diff)
    if output_path is None:
        sys.stdout.write(text)
    else:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
