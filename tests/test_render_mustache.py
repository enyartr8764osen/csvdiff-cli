"""Tests for csvdiff.render_mustache."""

from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_mustache import render_mustache


def _empty_diff(columns=None):
    return DiffResult(
        columns=columns or ["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert render_mustache(diff) == ""


def test_no_changes_produces_no_rows_messages():
    result = render_mustache(_empty_diff())
    assert "(no rows)" in result
    assert "{{#added}}" in result
    assert "{{#removed}}" in result
    assert "{{#changed}}" in result


def test_section_headers_present():
    result = render_mustache(_empty_diff())
    assert "{{#added}}" in result
    assert "{{/added}}" in result
    assert "{{#removed}}" in result
    assert "{{/removed}}" in result
    assert "{{#changed}}" in result
    assert "{{/changed}}" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_mustache(diff)
    added_block = result.split("{{#added}}")[1].split("{{/added}}")[0]
    assert "Alice" in added_block
    assert "1" in added_block


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_mustache(diff)
    removed_block = result.split("{{#removed}}")[1].split("{{/removed}}")[0]
    assert "Bob" in removed_block


def test_changed_row_shows_old_and_new():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[(old, new)],
    )
    result = render_mustache(diff)
    changed_block = result.split("{{#changed}}")[1].split("{{/changed}}")[0]
    assert "Carol" in changed_block
    assert "Caroline" in changed_block
    assert "->" in changed_block


def test_column_headers_appear_in_output():
    diff = DiffResult(
        columns=["id", "value"],
        added=[{"id": "10", "value": "x"}],
        removed=[],
        changed=[],
    )
    result = render_mustache(diff)
    assert "id" in result
    assert "value" in result
