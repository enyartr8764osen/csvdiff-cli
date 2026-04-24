"""Tests for csvdiff.render_pod."""

from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_pod import render_pod


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_pod(diff) == ""


def test_output_starts_with_pod_marker():
    result = render_pod(_empty_diff())
    assert "=pod" in result


def test_output_ends_with_cut_marker():
    result = render_pod(_empty_diff())
    assert "=cut" in result


def test_no_changes_produces_no_rows_messages():
    result = render_pod(_empty_diff())
    assert "No added rows." in result
    assert "No removed rows." in result
    assert "No changed rows." in result


def test_section_headers_present():
    result = render_pod(_empty_diff())
    assert "=head2 Added Rows" in result
    assert "=head2 Removed Rows" in result
    assert "=head2 Changed Rows" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_pod(diff)
    assert "Alice" in result
    assert "No added rows." not in result


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_pod(diff)
    assert "Bob" in result
    assert "No removed rows." not in result


def test_changed_row_shows_before_and_after():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(old, new)],
    )
    result = render_pod(diff)
    assert "Carol" in result
    assert "Caroline" in result
    assert "=head3 Before" in result
    assert "=head3 After" in result
    assert "No changed rows." not in result


def test_column_header_present_in_table():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_pod(diff)
    assert "id" in result
    assert "name" in result


def test_begin_text_block_used_for_table():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_pod(diff)
    assert "=begin text" in result
    assert "=end text" in result
