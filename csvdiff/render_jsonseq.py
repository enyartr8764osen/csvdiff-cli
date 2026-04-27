"""Render a DiffResult as RFC 7464 JSON Text Sequences (application/json-seq).

Each record is prefixed with the ASCII Record Separator (0x1E) and terminated
with a newline, making the output suitable for streaming consumers.
"""
from __future__ import annotations

import json
from typing import IO

from csvdiff.core import DiffResult

_RS = "\x1e"  # ASCII Record Separator (U+001E)


def _key_to_obj(key: tuple[str, ...], columns: list[str]) -> dict:
    """Convert a tuple key back to a dict using the key columns."""
    # key columns are not stored separately; derive from first key length
    return dict(zip(columns, key))


def render_jsonseq(
    diff: DiffResult,
    stream: IO[str],
    *,
    key_columns: list[str] | None = None,
    indent: int | None = None,
) -> None:
    """Write diff records to *stream* in JSON Text Sequence format.

    Each JSON object is prefixed with RS (0x1E) and followed by a newline.
    Objects carry a ``_status`` field of ``"added"``, ``"removed"``, or
    ``"changed"`` plus the row data (and for changed rows, ``_before`` and
    ``_after`` sub-objects).
    """
    columns = diff.columns

    def _emit(obj: dict) -> None:
        payload = json.dumps(obj, ensure_ascii=False, indent=indent)
        stream.write(_RS + payload + "\n")

    for key, row in diff.added.items():
        obj = {"_status": "added"}
        obj.update(row)
        _emit(obj)

    for key, row in diff.removed.items():
        obj = {"_status": "removed"}
        obj.update(row)
        _emit(obj)

    for key, (old_row, new_row) in diff.changed.items():
        obj = {
            "_status": "changed",
            "_before": old_row,
            "_after": new_row,
        }
        _emit(obj)
