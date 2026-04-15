"""Render diff results as JSON Lines (one JSON object per line)."""

import json
from typing import TextIO

from csvdiff.core import DiffResult, has_changes


def _key_to_obj(key: tuple) -> list:
    """Convert a tuple key to a JSON-serialisable list."""
    return list(key)


def render_jsonlines(diff: DiffResult, out: TextIO) -> None:
    """
    Write each change as a single JSON object on its own line.

    Schema per line:
      {"type": "added",   "key": [...], "row": {...}}
      {"type": "removed", "key": [...], "row": {...}}
      {"type": "changed", "key": [...], "old": {...}, "new": {...},
       "fields": ["col1", ...]}

    If there are no changes nothing is written.
    """
    if not has_changes(diff):
        return

    for key, row in diff.added.items():
        record = {
            "type": "added",
            "key": _key_to_obj(key),
            "row": row,
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")

    for key, row in diff.removed.items():
        record = {
            "type": "removed",
            "key": _key_to_obj(key),
            "row": row,
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")

    for key, (old_row, new_row) in diff.changed.items():
        changed_fields = [
            col for col in old_row if old_row.get(col) != new_row.get(col)
        ]
        record = {
            "type": "changed",
            "key": _key_to_obj(key),
            "old": old_row,
            "new": new_row,
            "fields": changed_fields,
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
