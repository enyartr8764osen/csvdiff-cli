"""Tests for csvdiff.render_ini."""
from __future__ import annotations

import configparser
import io
from typing import Dict, List

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_ini import render_ini, _escape_value


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# _escape_value
# ---------------------------------------------------------------------------

def test_escape_value_plain_string_unchanged():
    assert _escape_value("hello") == "hello"


def test_escape_value_backslash_escaped():
    assert _escape_value("a\\b") == "a\\\\b"


def test_escape_value_newline_escaped():
    assert _escape_value("a\nb") == "a\\nb"


# ---------------------------------------------------------------------------
# render_ini
# ---------------------------------------------------------------------------

def test_no_columns_returns_empty_string():
    assert render_ini(_empty_diff(), []) == ""


def test_no_changes_produces_four_sections():
    result = render_ini(_empty_diff(), ["id", "name"])
    for section in ("added", "removed", "changed_old", "changed_new"):
        assert f"[{section}]" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_ini(diff, ["id", "name"])
    lines = result.splitlines()
    added_idx = next(i for i, l in enumerate(lines) if l == "[added]")
    section_lines = lines[added_idx:]
    assert any("id = 1" in l for l in section_lines)
    assert any("name = Alice" in l for l in section_lines)


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_ini(diff, ["id", "name"])
    assert "[removed]" in result
    assert "name = Bob" in result


def test_changed_row_appears_in_changed_sections():
    diff = DiffResult(
        added=[],
        removed=[],
        changed=[
            {"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Carole"}}
        ],
    )
    result = render_ini(diff, ["id", "name"])
    assert "[changed_old]" in result
    assert "[changed_new]" in result
    assert "name = Carol" in result
    assert "name = Carole" in result


def test_empty_sections_contain_no_rows_comment():
    result = render_ini(_empty_diff(), ["id"])
    assert "; (no rows)" in result


def test_entry_index_comments_present_for_multiple_rows():
    diff = DiffResult(
        added=[{"id": "1"}, {"id": "2"}],
        removed=[],
        changed=[],
    )
    result = render_ini(diff, ["id"])
    assert "; entry 0" in result
    assert "; entry 1" in result
