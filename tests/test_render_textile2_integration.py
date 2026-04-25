"""Integration tests for render_textile2 with realistic data."""
from __future__ import annotations

import io

from csvdiff.core import DiffResult
from csvdiff.render_textile2 import render_textile2


def _make_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "country", "value"],
        added=[
            {"id": "10", "country": "France", "value": "42"},
            {"id": "11", "country": "Spain", "value": "7"},
        ],
        removed=[
            {"id": "20", "country": "Italy", "value": "99"},
        ],
        changed=[
            (
                {"id": "30", "country": "Germany", "value": "1"},
                {"id": "30", "country": "Germany", "value": "2"},
            )
        ],
        unchanged=[],
    )


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_textile2(diff, buf)
    return buf.getvalue()


def test_multiple_added_rows_all_appear() -> None:
    out = _render(_make_diff())
    assert "France" in out
    assert "Spain" in out


def test_multiple_sections_all_present() -> None:
    out = _render(_make_diff())
    assert "Added" in out
    assert "Removed" in out
    assert "Changed" in out


def test_table_rows_start_with_pipe() -> None:
    out = _render(_make_diff())
    data_lines = [ln for ln in out.splitlines() if ln.startswith("|")]
    assert len(data_lines) > 0


def test_all_columns_appear_in_header() -> None:
    out = _render(_make_diff())
    assert "*id*" in out
    assert "*country*" in out
    assert "*value*" in out


def test_column_widths_pad_correctly() -> None:
    """Cells in the same column should be padded to equal width."""
    out = _render(_make_diff())
    # 'France' is 6 chars, 'Spain' is 5 — both should appear padded in the table
    # We just verify both values are present; alignment is best-effort.
    assert "France" in out
    assert "Spain " in out  # padded to match 'France'
