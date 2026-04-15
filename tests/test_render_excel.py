"""Tests for csvdiff.render_excel."""
from __future__ import annotations

import os
import tempfile

import pytest

openpyxl = pytest.importorskip("openpyxl")

from csvdiff.core import DiffResult
from csvdiff.render_excel import render_excel


COLUMNS = ["id", "name", "score"]


def _empty_diff() -> DiffResult:
    return DiffResult(columns=COLUMNS, added=[], removed=[], changed=[])


def _tmp_xlsx():
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    return path


def test_no_changes_produces_empty_sheets():
    path = _tmp_xlsx()
    try:
        render_excel(_empty_diff(), path)
        wb = openpyxl.load_workbook(path)
        assert set(wb.sheetnames) == {"Added", "Removed", "Changed"}
        # Only the header row should be present
        assert wb["Added"].max_row == 1
        assert wb["Removed"].max_row == 1
        assert wb["Changed"].max_row == 1
    finally:
        os.unlink(path)


def test_added_row_appears_in_added_sheet():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "score": "95"})
    path = _tmp_xlsx()
    try:
        render_excel(diff, path)
        ws = openpyxl.load_workbook(path)["Added"]
        assert ws.max_row == 2
        values = [ws.cell(row=2, column=i).value for i in range(1, 4)]
        assert values == ["1", "Alice", "95"]
    finally:
        os.unlink(path)


def test_removed_row_appears_in_removed_sheet():
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob", "score": "80"})
    path = _tmp_xlsx()
    try:
        render_excel(diff, path)
        ws = openpyxl.load_workbook(path)["Removed"]
        assert ws.max_row == 2
        values = [ws.cell(row=2, column=i).value for i in range(1, 4)]
        assert values == ["2", "Bob", "80"]
    finally:
        os.unlink(path)


def test_changed_row_appears_in_changed_sheet():
    diff = _empty_diff()
    old = {"id": "3", "name": "Carol", "score": "70"}
    new = {"id": "3", "name": "Carol", "score": "85"}
    diff.changed.append((old, new))
    path = _tmp_xlsx()
    try:
        render_excel(diff, path)
        ws = openpyxl.load_workbook(path)["Changed"]
        assert ws.max_row == 2
        # old columns first, then new columns (6 total)
        old_score = ws.cell(row=2, column=3).value   # score (old)
        new_score = ws.cell(row=2, column=6).value   # score (new)
        assert old_score == "70"
        assert new_score == "85"
    finally:
        os.unlink(path)


def test_header_row_contains_column_names():
    path = _tmp_xlsx()
    try:
        render_excel(_empty_diff(), path)
        wb = openpyxl.load_workbook(path)
        for sheet_name in ("Added", "Removed"):
            ws = wb[sheet_name]
            headers = [ws.cell(row=1, column=i).value for i in range(1, 4)]
            assert headers == COLUMNS
        ws_c = wb["Changed"]
        headers = [ws_c.cell(row=1, column=i).value for i in range(1, 7)]
        assert headers == [f"{c} (old)" for c in COLUMNS] + [f"{c} (new)" for c in COLUMNS]
    finally:
        os.unlink(path)
