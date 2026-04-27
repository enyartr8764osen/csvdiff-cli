"""Render diff as a CSV with inline change markers (before/after columns)."""
from __future__ import annotations

import csv
import io
from typing import List

from csvdiff.core import DiffResult


def render_csv3(diff: DiffResult, columns: List[str], *, delimiter: str = ",") -> str:
    """Return a CSV string with a _status column and before/after pairs for changed rows.

    Rows are emitted with a ``_status`` column (``added``, ``removed``, or
    ``changed``) followed by all data columns.  For *changed* rows two rows are
    written: one tagged ``changed:before`` and one tagged ``changed:after`` so
    that a plain CSV consumer can still diff them without losing information.
    """
    if not columns:
        return ""

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter)

    header = ["_status"] + list(columns)
    writer.writerow(header)

    for row in diff.added:
        writer.writerow(["added"] + [row.get(c, "") for c in columns])

    for row in diff.removed:
        writer.writerow(["removed"] + [row.get(c, "") for c in columns])

    for old_row, new_row in diff.changed:
        writer.writerow(["changed:before"] + [old_row.get(c, "") for c in columns])
        writer.writerow(["changed:after"] + [new_row.get(c, "") for c in columns])

    return buf.getvalue()
