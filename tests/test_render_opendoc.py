"""Tests for render_opendoc (ODS output)."""
from __future__ import annotations

import pytest
from pathlib import Path
from typing import Dict, List

from csvdiff.core import DiffResult

odfpy = pytest.importorskip("odf", reason="odfpy not installed")

from csvdiff.render_opendoc import render_opendoc  # noqa: E402


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _tmp_ods(tmp_path: Path) -> Path:
    return tmp_path / "out.ods"


def _sheet_rows(doc, sheet_name: str) -> List[List[str]]:
    """Return all rows (as lists of strings) from the named sheet."""
    from odf.table import Table, TableRow, TableCell
    from odf.text import P

    for sheet in doc.spreadsheet.getElementsByType(Table):
        if sheet.getAttribute("name") == sheet_name:
            rows = []
            for tr in sheet.getElementsByType(TableRow):
                cells = []
                for cell in tr.getElementsByType(TableCell):
                    texts = cell.getElementsByType(P)
                    cells.append(texts[0].firstChild.data if texts else "")
                rows.append(cells)
            return rows
    return []


def _load(path: Path):
    from odf.opendocument import load
    return load(str(path))


def test_no_changes_produces_empty_sheets(tmp_path: Path) -> None:
    dest = _tmp_ods(tmp_path)
    render_opendoc(_empty_diff(), dest)
    doc = _load(dest)
    # Each sheet should have only a header row
    for sheet_name in ("Added", "Removed", "Changed (before)", "Changed (after)"):
        rows = _sheet_rows(doc, sheet_name)
        assert len(rows) == 1, f"{sheet_name} should have header only"


def test_added_row_appears_in_added_sheet(tmp_path: Path) -> None:
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    dest = _tmp_ods(tmp_path)
    render_opendoc(diff, dest)
    doc = _load(dest)
    rows = _sheet_rows(doc, "Added")
    assert len(rows) == 2
    assert rows[1] == ["1", "Alice"]


def test_removed_row_appears_in_removed_sheet(tmp_path: Path) -> None:
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    dest = _tmp_ods(tmp_path)
    render_opendoc(diff, dest)
    doc = _load(dest)
    rows = _sheet_rows(doc, "Removed")
    assert len(rows) == 2
    assert rows[1] == ["2", "Bob"]


def test_changed_row_appears_in_before_and_after_sheets(tmp_path: Path) -> None:
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(old, new)],
    )
    dest = _tmp_ods(tmp_path)
    render_opendoc(diff, dest)
    doc = _load(dest)
    before_rows = _sheet_rows(doc, "Changed (before)")
    after_rows = _sheet_rows(doc, "Changed (after)")
    assert before_rows[1] == ["3", "Carol"]
    assert after_rows[1] == ["3", "Caroline"]


def test_output_creates_parent_dirs(tmp_path: Path) -> None:
    dest = tmp_path / "subdir" / "nested" / "out.ods"
    render_opendoc(_empty_diff(), dest)
    assert dest.exists()
