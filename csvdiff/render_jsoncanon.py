"""Render diff results as canonical JSON (RFC 8785-style, sorted keys)."""

from __future__ import annotations

import json
from typing import IO

from csvdiff.core import DiffResult


def _row_to_obj(row: dict[str, str]) -> dict[str, str]:
    """Return a copy of *row* with keys in sorted order."""
    return {k: row[k] for k in sorted(row)}


def _key_to_obj(key: tuple[str, ...], columns: list[str]) -> dict[str, str]:
    """Convert a key tuple back to a sorted dict using the key column names."""
    return {columns[i]: key[i] for i in range(len(columns))}


def render_jsoncanon(
    diff: DiffResult,
    stream: IO[str],
    *,
    key_columns: list[str] | None = None,
    indent: int | None = 2,
) -> None:
    """Write a canonical JSON representation of *diff* to *stream*.

    The output is a single JSON object with three top-level arrays:
    ``added``, ``removed``, and ``changed``.  All object keys are sorted
    alphabetically so that the output is stable across Python versions.
    """
    key_columns = key_columns or []

    added = [
        {"key": _key_to_obj(k, key_columns), "row": _row_to_obj(row)}
        for k, row in sorted(diff.added.items())
    ]

    removed = [
        {"key": _key_to_obj(k, key_columns), "row": _row_to_obj(row)}
        for k, row in sorted(diff.removed.items())
    ]

    changed = [
        {
            "key": _key_to_obj(k, key_columns),
            "old": _row_to_obj(old),
            "new": _row_to_obj(new),
        }
        for k, (old, new) in sorted(diff.changed.items())
    ]

    payload: dict = {
        "added": added,
        "changed": changed,
        "removed": removed,
    }

    json.dump(payload, stream, indent=indent, sort_keys=True, ensure_ascii=False)
    stream.write("\n")
