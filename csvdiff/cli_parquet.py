"""CLI handler for Parquet output format."""
from __future__ import annotations

from pathlib import Path

from csvdiff.core import DiffResult


def handle_parquet_output(diff: DiffResult, output_path: str | None) -> None:
    """Write *diff* to a Parquet file.

    Parameters
    ----------
    diff:
        The computed diff result.
    output_path:
        Destination ``.parquet`` file path.  If ``None`` or empty a
        ``ValueError`` is raised because Parquet is a binary format and
        cannot be streamed to stdout.
    """
    if not output_path:
        raise ValueError(
            "Parquet output requires an explicit --output path "
            "(binary format cannot be written to stdout)."
        )

    try:
        from csvdiff.render_parquet import render_parquet
    except ImportError as exc:
        raise SystemExit(
            f"Cannot produce Parquet output: {exc}"
        ) from exc

    dest = Path(output_path)
    render_parquet(diff, dest)
    print(f"Parquet diff written to {dest}")
