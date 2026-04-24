"""Render a DiffResult as JSON Lines (one JSON object per line).

Each line is a self-contained JSON object with the shape::

    {"status": "added"|"removed"|"changed",
     "key": {col: val, ...},
     "row": {col: val, ...}}          # for added / removed

    {"status": "changed",
     "key": {col: val, ...},
     "before": {col: val, ...},
     "after":  {col: val, ...}}       # for changed
"""

from __future__ import annotations

import json
from io import StringIO
from typing import List

from csvdiff.core import DiffResult


def _key_to_obj(key_cols: List[str], row: dict) -> dict:
    """Return a dict containing only the key columns from *row*."""
    return {col: row[col] for col in key_cols if col in row}


def render_jsonl(
    diff: DiffResult,
    key_cols: List[str],
    *,
    stream=None,
) -> str:
    """Render *diff* as JSON Lines and return the result as a string.

    If *stream* is provided the output is also written there.
    """
    buf = StringIO()

    for row in diff.added:
        obj = {
            "status": "added",
            "key": _key_to_obj(key_cols, row),
            "row": row,
        }
        buf.write(json.dumps(obj, ensure_ascii=False) + "\n")

    for row in diff.removed:
        obj = {
            "status": "removed",
            "key": _key_to_obj(key_cols, row),
            "row": row,
        }
        buf.write(json.dumps(obj, ensure_ascii=False) + "\n")

    for before, after in diff.changed:
        obj = {
            "status": "changed",
            "key": _key_to_obj(key_cols, before),
            "before": before,
            "after": after,
        }
        buf.write(json.dumps(obj, ensure_ascii=False) + "\n")

    result = buf.getvalue()
    if stream is not None:
        stream.write(result)
    return result
