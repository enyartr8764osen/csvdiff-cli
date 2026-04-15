"""Render a DiffResult as newline-delimited JSON (NDJSON / JSON Lines variant
that groups records by change type rather than emitting one record per row).

Each output line is a self-contained JSON object with the shape::

    {"type": "added"|"removed"|"changed", "key": [...], "row": {...}}

For *changed* rows both ``old`` and ``new`` sub-objects are included instead
of a single ``row`` key::

    {"type": "changed", "key": [...], "old": {...}, "new": {...}}
"""

from __future__ import annotations

import json
from typing import IO, List

from csvdiff.core import DiffResult


def _key_to_list(key: tuple) -> List[str]:
    """Convert a tuple key to a JSON-serialisable list."""
    return list(key)


def render_ndjson(diff: DiffResult, stream: IO[str]) -> None:
    """Write NDJSON representation of *diff* to *stream*.

    Lines are written in the order: added rows, removed rows, changed rows.
    If there are no changes nothing is written.
    """
    for key, row in diff.added.items():
        obj = {"type": "added", "key": _key_to_list(key), "row": dict(row)}
        stream.write(json.dumps(obj, ensure_ascii=False) + "\n")

    for key, row in diff.removed.items():
        obj = {"type": "removed", "key": _key_to_list(key), "row": dict(row)}
        stream.write(json.dumps(obj, ensure_ascii=False) + "\n")

    for key, (old_row, new_row) in diff.changed.items():
        obj = {
            "type": "changed",
            "key": _key_to_list(key),
            "old": dict(old_row),
            "new": dict(new_row),
        }
        stream.write(json.dumps(obj, ensure_ascii=False) + "\n")
