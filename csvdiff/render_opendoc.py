"""Render a DiffResult as an OpenDocument Spreadsheet (.ods) file."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from csvdiff.core import DiffResult

_SECTION_LABELS: List[Tuple[str, str]] = [
    ("added", "Added"),
    ("removed", "Removed"),
    ("changed", "Changed"),
]


def _header_row(columns: List[str]) -> List[str]:
    return list(columns)


def _write_sheet(
    sheet,
    label: str,
    columns: List[str],
    rows: List[Dict[str, str]],
) -> None:
    """Write a header + data rows into *sheet*."""
    try:
        from odf.table import TableRow, TableCell
        from odf.text import P
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "odfpy is required for ODS output: pip install odfpy"
        ) from exc

    header = TableRow()
    for col in columns:
        cell = TableCell(valuetype="string")
        cell.addElement(P(text=col))
        header.addElement(cell)
    sheet.addElement(header)

    for row in rows:
        tr = TableRow()
        for col in columns:
            cell = TableCell(valuetype="string")
            cell.addElement(P(text=row.get(col, "")))
            tr.addElement(cell)
        sheet.addElement(tr)


def render_opendoc(diff: DiffResult, path: Path) -> None:
    """Write *diff* to an ODS workbook at *path*."""
    try:
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "odfpy is required for ODS output: pip install odfpy"
        ) from exc

    doc = OpenDocumentSpreadsheet()
    columns = diff.columns

    changed_old = [old for old, _new in diff.changed]
    changed_new = [new for _old, new in diff.changed]

    section_data = {
        "added": diff.added,
        "removed": diff.removed,
        "changed_before": changed_old,
        "changed_after": changed_new,
    }

    for sheet_name, rows in [
        ("Added", diff.added),
        ("Removed", diff.removed),
        ("Changed (before)", changed_old),
        ("Changed (after)", changed_new),
    ]:
        sheet = Table(name=sheet_name)
        _write_sheet(sheet, sheet_name, columns, rows)
        doc.spreadsheet.addElement(sheet)

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
