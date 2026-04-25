"""Render diff results as JSON Patch (RFC 6902) documents."""
from __future__ import annotations

import json
from typing import IO

from csvdiff.core import DiffResult


def _key_to_path_segment(key: tuple[str, ...]) -> str:
    """Convert a row key tuple to a URL-safe path segment."""
    return "/".join(str(k).replace("~", "~0").replace("/", "~1") for k in key)


def _row_to_obj(row: dict[str, str]) -> dict[str, str]:
    return dict(row)


def render_jsonpatch(
    diff: DiffResult,
    stream: IO[str],
    *,
    pretty: bool = False,
) -> None:
    """Write a JSON Patch array to *stream* representing *diff*.

    - Added rows become ``add`` operations under ``/added/<key>``.
    - Removed rows become ``remove`` operations under ``/removed/<key>``.
    - Changed rows become ``replace`` operations under ``/changed/<key>``.
    """
    ops: list[dict] = []

    for key, row in diff.added.items():
        seg = _key_to_path_segment(key)
        ops.append({
            "op": "add",
            "path": f"/added/{seg}",
            "value": _row_to_obj(row),
        })

    for key, row in diff.removed.items():
        seg = _key_to_path_segment(key)
        ops.append({
            "op": "remove",
            "path": f"/removed/{seg}",
            "value": _row_to_obj(row),
        })

    for key, (old_row, new_row) in diff.changed.items():
        seg = _key_to_path_segment(key)
        ops.append({
            "op": "replace",
            "path": f"/changed/{seg}",
            "value": {
                "before": _row_to_obj(old_row),
                "after": _row_to_obj(new_row),
            },
        })

    indent = 2 if pretty else None
    json.dump(ops, stream, indent=indent, ensure_ascii=False)
    stream.write("\n")
