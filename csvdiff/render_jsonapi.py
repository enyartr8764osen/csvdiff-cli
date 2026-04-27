"""Render a DiffResult as a JSON:API-compatible document."""
from __future__ import annotations

import json
from typing import IO

from csvdiff.core import DiffResult


def _row_to_resource(row: dict, row_type: str, index: int) -> dict:
    """Convert a CSV row dict to a JSON:API resource object."""
    return {
        "type": row_type,
        "id": str(index),
        "attributes": dict(row),
    }


def _changed_to_resource(old: dict, new: dict, index: int) -> dict:
    """Convert a changed-row pair to a JSON:API resource object."""
    columns = list(old.keys())
    changed_fields = [c for c in columns if old.get(c) != new.get(c)]
    return {
        "type": "changed",
        "id": str(index),
        "attributes": {
            "before": dict(old),
            "after": dict(new),
            "changed_fields": changed_fields,
        },
    }


def render_jsonapi(
    diff: DiffResult,
    stream: IO[str],
    *,
    indent: int = 2,
) -> None:
    """Write a JSON:API document describing *diff* to *stream*."""
    data: list[dict] = []

    for i, row in enumerate(diff.added):
        data.append(_row_to_resource(row, "added", i))

    for i, row in enumerate(diff.removed):
        data.append(_row_to_resource(row, "removed", i))

    for i, (old, new) in enumerate(diff.changed):
        data.append(_changed_to_resource(old, new, i))

    doc = {
        "data": data,
        "meta": {
            "added": len(diff.added),
            "removed": len(diff.removed),
            "changed": len(diff.changed),
            "total": len(data),
        },
    }
    json.dump(doc, stream, indent=indent)
    stream.write("\n")
