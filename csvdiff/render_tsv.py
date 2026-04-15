"""Render diff results as TSV (tab-separated values)."""

from __future__ import annotations

import csv
import io
from typing import List

from csvdiff.core import DiffResult

_STATUS_ADDED = "added"
_STATUS_REMOVED = "removed"
_STATUS_CHANGED_OLD = "changed_old"
_STATUS_CHANGED_NEW = "changed_new"


def render_tsv(diff: DiffResult, columns: List[str]) -> str:
    """Return a TSV string representing *diff*.

    Each output row is prefixed with a ``_status`` column that contains one of:
    ``added``, ``removed``, ``changed_old``, or ``changed_new``.

    Returns an empty string when there are no changes.
    """
    if not diff.added and not diff.removed and not diff.changed:
        return ""

    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")

    header = ["_status"] + list(columns)
    writer.writerow(header)

    for row in diff.added:
        writer.writerow([_STATUS_ADDED] + [row.get(c, "") for c in columns])

    for row in diff.removed:
        writer.writerow([_STATUS_REMOVED] + [row.get(c, "") for c in columns])

    for old_row, new_row in diff.changed:
        writer.writerow([_STATUS_CHANGED_OLD] + [old_row.get(c, "") for c in columns])
        writer.writerow([_STATUS_CHANGED_NEW] + [new_row.get(c, "") for c in columns])

    return output.getvalue()
