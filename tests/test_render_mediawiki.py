"""Tests for csvdiff.render_mediawiki."""

from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_mediawiki import render_mediawiki


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_changes_produces_empty_string():
    result = render_mediawiki(_empty_diff())
    assert result == ""


def test_added_row_appears_in_added_section():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    result = render_mediawiki(diff)
    assert "== Added Rows ==" in result
    assert "Alice" in result


def test_removed_row_appears_in_removed_section():
    diff = _empty_diff()
    diff.removed.append({"id": "2", "name": "Bob"})
    result = render_mediawiki(diff)
    assert "== Removed Rows ==" in result
    assert "Bob" in result


def test_changed_row_shows_old_and_new():
    diff = _empty_diff()
    diff.changed.append(
        {"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}
    )
    result = render_mediawiki(diff)
    assert "== Changed Rows (before) ==" in result
    assert "== Changed Rows (after) ==" in result
    assert "Carol" in result
    assert "Caroline" in result


def test_wikitable_class_present():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    result = render_mediawiki(diff)
    assert 'class="wikitable"' in result


def test_header_row_uses_exclamation_marks():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    result = render_mediawiki(diff)
    lines = result.splitlines()
    header_lines = [l for l in lines if l.startswith("!")]
    assert header_lines, "Expected at least one header line starting with '!'"
    assert "id" in header_lines[0]
    assert "name" in header_lines[0]


def test_no_added_section_when_only_removed():
    diff = _empty_diff()
    diff.removed.append({"id": "5", "name": "Eve"})
    result = render_mediawiki(diff)
    assert "== Added Rows ==" not in result
    assert "== Removed Rows ==" in result


def test_empty_sections_omitted():
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    result = render_mediawiki(diff)
    assert "== Removed Rows ==" not in result
    assert "== Changed Rows" not in result
