"""Render a DiffResult as a JSON-stat 2.0 dataset.

JSON-stat is a simple lightweight JSON dissemination format best suited
for data tables.  We encode added/removed/changed rows as a minimal
dataset with a ``status`` dimension.

See https://json-stat.org/ for the specification.
"""
from __future__ import annotations

import json
from typing import IO

from csvdiff.core import DiffResult


def _row_to_obj(row: dict[str, str], status: str) -> dict:
    obj = {"status": status}
    obj.update(row)
    return obj


def render_jsonstat(diff: DiffResult, stream: IO[str]) -> None:
    """Write a JSON-stat 2.0 dataset to *stream*.

    The dataset contains one value array entry per changed row.  Each
    observation carries a ``status`` label (``added``, ``removed``,
    ``old``, or ``new``) plus all CSV column values.
    """
    columns = diff.columns
    if not columns:
        stream.write(json.dumps({"version": "2.0", "class": "dataset",
                                  "id": [], "size": [], "value": []}))
        return

    rows: list[dict] = []

    for row in diff.added:
        rows.append(_row_to_obj(row, "added"))

    for row in diff.removed:
        rows.append(_row_to_obj(row, "removed"))

    for old_row, new_row in diff.changed:
        rows.append(_row_to_obj(old_row, "old"))
        rows.append(_row_to_obj(new_row, "new"))

    dims = ["status"] + list(columns)
    status_vals = sorted({r["status"] for r in rows}) if rows else []
    col_vals: dict[str, list[str]] = {c: [] for c in columns}
    for row in rows:
        for col in columns:
            v = row.get(col, "")
            if v not in col_vals[col]:
                col_vals[col].append(v)

    ids = dims
    sizes = [len(status_vals)] + [len(col_vals[c]) for c in columns]

    dataset = {
        "version": "2.0",
        "class": "dataset",
        "id": ids,
        "size": sizes,
        "dimension": {
            "status": {"label": "status", "category": {
                "index": {v: i for i, v in enumerate(status_vals)},
                "label": {v: v for v in status_vals},
            }},
            **{
                col: {"label": col, "category": {
                    "index": {v: i for i, v in enumerate(col_vals[col])},
                    "label": {v: v for v in col_vals[col]},
                }}
                for col in columns
            },
        },
        "value": [
            [r.get(col, "") for col in columns]
            for r in rows
        ],
        "extension": {
            "status_column": [r["status"] for r in rows],
        },
    }

    json.dump(dataset, stream, indent=2)
