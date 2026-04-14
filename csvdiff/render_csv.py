"""CSV output renderer for diff results."""

import csv
import io
from typing import TextIO

from csvdiff.core import DiffResult

# Status column name written into the output CSV
STATUS_COLUMN = "_diff_status"


def render_csv(diff: DiffResult, out: TextIO, delimiter: str = ",") -> None:
    """Write diff results as a CSV file to *out*.

    Each row is annotated with a ``_diff_status`` column whose value is one of:
    ``added``, ``removed``, or ``modified``.

    For modified rows both the *old* and *new* versions are written with
    column names suffixed ``_old`` / ``_new`` for changed fields.

    Args:
        diff: A :class:`~csvdiff.core.DiffResult` instance.
        out: A writable text stream.
        delimiter: CSV field delimiter (default comma).
    """
    rows_out = []

    for key, row in diff.added.items():
        rows_out.append({STATUS_COLUMN: "added", **row})

    for key, row in diff.removed.items():
        rows_out.append({STATUS_COLUMN: "removed", **row})

    for key, change in diff.modified.items():
        flat: dict = {STATUS_COLUMN: "modified"}
        old_row, new_row = change
        all_cols = list(old_row.keys())
        for col in all_cols:
            old_val = old_row.get(col, "")
            new_val = new_row.get(col, "")
            if old_val != new_val:
                flat[f"{col}_old"] = old_val
                flat[f"{col}_new"] = new_val
            else:
                flat[col] = old_val
        rows_out.append(flat)

    if not rows_out:
        return

    # Collect all field names preserving insertion order
    fieldnames: list = []
    seen: set = set()
    for row in rows_out:
        for k in row:
            if k not in seen:
                fieldnames.append(k)
                seen.add(k)

    writer = csv.DictWriter(
        out,
        fieldnames=fieldnames,
        delimiter=delimiter,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows_out)
