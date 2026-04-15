"""Tests for the HTML renderer."""

import pytest
from csvdiff.core import DiffResult
from csvdiff.render_html import render_html


def _empty_diff(headers=None):
    return DiffResult(
        headers=headers or ["id", "name", "value"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_changes_produces_no_diff_message():
    result = render_html(_empty_diff())
    assert "no-changes" in result
    assert "No differences found" in result


def test_added_row_appears_in_added_section():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "10"})
    result = render_html(diff)
    assert "Added Rows" in result
    assert "Alice" in result
    assert 'class=\'added\'' in result


def test_removed_row_appears_in_removed_section():
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob", "value": "20"})
    result = render_html(diff)
    assert "Removed Rows" in result
    assert "Bob" in result
    assert 'class=\'removed\'' in result


def test_changed_row_shows_old_and_new():
    diff = _empty_diff()
    diff.changed.append({
        "old": {"id": "3", "name": "Carol", "value": "30"},
        "new": {"id": "3", "name": "Carol", "value": "99"},
    })
    result = render_html(diff)
    assert "Changed Rows (Before)" in result
    assert "Changed Rows (After)" in result
    assert "30" in result
    assert "99" in result


def test_html_escapes_special_characters():
    diff = _empty_diff(headers=["id", "name", "value"])
    diff.added.append({"id": "4", "name": "<script>alert(1)</script>", "value": "&"})
    result = render_html(diff)
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "&amp;" in result


def test_output_is_valid_html_structure():
    diff = _empty_diff()
    diff.added.append({"id": "5", "name": "Dave", "value": "50"})
    result = render_html(diff)
    assert result.startswith("<!DOCTYPE html>")
    assert "<html>" in result
    assert "</html>" in result
    assert "<table>" in result
    assert "<thead>" in result
    assert "<tbody>" in result


def test_headers_appear_in_table_header():
    diff = _empty_diff(headers=["sku", "price", "stock"])
    diff.removed.append({"sku": "ABC", "price": "9.99", "stock": "5"})
    result = render_html(diff)
    assert "<th>sku</th>" in result
    assert "<th>price</th>" in result
    assert "<th>stock</th>" in result


def test_multiple_sections_present_when_all_change_types_exist():
    """Verify that added, removed, and changed sections all appear together."""
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice", "value": "10"})
    diff.removed.append({"id": "2", "name": "Bob", "value": "20"})
    diff.changed.append({
        "old": {"id": "3", "name": "Carol", "value": "30"},
        "new": {"id": "3", "name": "Carol", "value": "99"},
    })
    result = render_html(diff)
    assert "Added Rows" in result
    assert "Removed Rows" in result
    assert "Changed Rows (Before)" in result
    assert "Changed Rows (After)" in result
    assert "no-changes" not in result
