"""Render a DiffResult as newline-delimited JSON (one envelope per change).

Each line is a self-contained JSON object with the shape::

    {"status": "added"|"removed"|"changed", "key": {...}, "row": {...}}

For ``changed`` rows both ``old`` and ``new`` sub-objects are included
instead of a single ``row`` key.
"""
from __future__ import annotations

import json
from typing import IO

from csvdiff.core import DiffResult


def _key_to_obj(key: tuple, columns: list[str]) -> dict:
    """Return a dict mapping key-column names to their values."""
    # key length may be shorter than columns when only some cols are keys;
    # we store positional key values without column names when columns is empty.
    if not columns:
        return {str(i): v for i, v in enumerate(key)}
    return dict(zip(columns, key))


def render_jsonnd(
    diff: DiffResult,
    stream: IO[str],
    *,
    key_columns: list[str] | None = None,
    indent: int | None = None,
) -> None:
    """Write one JSON object per changed row to *stream*.

    Parameters
    ----------
    diff:
        The diff result to serialise.
    stream:
        A writable text stream.
    key_columns:
        Column names that form the row key (used to populate the ``key``
        field).  Defaults to an empty list.
    indent:
        If given, each JSON object is pretty-printed with this indent level.
        The output is no longer strictly newline-delimited in that case, but
        it is useful for debugging.
    """
    key_columns = key_columns or []
    sep = "\n"

    def _emit(obj: dict) -> None:
        stream.write(json.dumps(obj, indent=indent))
        stream.write(sep)

    for key, row in diff.added:
        _emit({
            "status": "added",
            "key": _key_to_obj(key, key_columns),
            "row": dict(zip(diff.columns, row)),
        })

    for key, row in diff.removed:
        _emit({
            "status": "removed",
            "key": _key_to_obj(key, key_columns),
            "row": dict(zip(diff.columns, row)),
        })

    for key, old_row, new_row in diff.changed:
        _emit({
            "status": "changed",
            "key": _key_to_obj(key, key_columns),
            "old": dict(zip(diff.columns, old_row)),
            "new": dict(zip(diff.columns, new_row)),
        })
