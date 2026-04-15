"""CLI helper for the SQL output format."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO, List

from csvdiff.core import DiffResult
from csvdiff.render_sql import render_sql


def handle_sql_output(
    diff: DiffResult,
    table: str,
    key_columns: List[str],
    output_path: str | None,
) -> None:
    """Render *diff* as SQL and write to *output_path* or stdout."""
    if output_path:
        path = Path(output_path)
        with path.open("w", encoding="utf-8", newline="") as fh:
            render_sql(diff, table=table, out=fh, key_columns=key_columns)
    else:
        _render_to_stream(diff, table=table, key_columns=key_columns, stream=sys.stdout)


def _render_to_stream(
    diff: DiffResult,
    table: str,
    key_columns: List[str],
    stream: IO[str],
) -> None:
    render_sql(diff, table=table, out=stream, key_columns=key_columns)
