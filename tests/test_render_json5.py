"""Tests for csvdiff.render_json5."""
from __future__ import annotations

import json
import re
from typing import Dict, List, Tuple

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_json5 import render_json5


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _strip_comments(text: str) -> str:
    """Remove // … comments so the result can be parsed as plain JSON."""
    lines = [re.sub(r"//.*$", "", line) for line in text.splitlines()]
    # also strip trailing commas before ] or } to make it valid JSON
    cleaned = "\n".join(lines)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    return cleaned


def _parse(text: str) -> dict:
    return json.loads(_strip_comments(text))


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_empty_diff_has_three_sections():
    result = render_json5(_empty_diff())
    data = _parse(result)
    assert set(data.keys()) == {"added", "removed", "changed"}


def test_empty_diff_all_sections_are_lists():
    result = render_json5(_empty_diff())
    data = _parse(result)
    assert data["added"] == []
    assert data["removed"] == []
    assert data["changed"] == []


def test_no_columns_returns_empty_structure():
    result = render_json5(_empty_diff(), columns=[])
    assert "added" in result
    assert "removed" in result
    assert "changed" in result


def test_added_row_appears_in_added_section():
    row = {"id": "1", "name": "Alice"}
    diff = DiffResult(added=[row], removed=[], changed=[])
    data = _parse(render_json5(diff))
    assert len(data["added"]) == 1
    assert data["added"][0]["id"] == "1"
    assert data["added"][0]["name"] == "Alice"


def test_removed_row_appears_in_removed_section():
    row = {"id": "2", "name": "Bob"}
    diff = DiffResult(added=[], removed=[row], changed=[])
    data = _parse(render_json5(diff))
    assert len(data["removed"]) == 1
    assert data["removed"][0]["name"] == "Bob"


def test_changed_row_shows_new_values():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(added=[], removed=[], changed=[(old, new)])
    data = _parse(render_json5(diff))
    assert len(data["changed"]) == 1
    assert data["changed"][0]["name"] == "Caroline"


def test_output_contains_comments():
    row = {"id": "1", "x": "y"}
    diff = DiffResult(added=[row], removed=[], changed=[])
    result = render_json5(diff)
    assert "//" in result


def test_output_ends_with_newline():
    result = render_json5(_empty_diff())
    assert result.endswith("\n")


def test_special_characters_are_escaped():
    row = {"id": "1", "val": 'say "hello"'}
    diff = DiffResult(added=[row], removed=[], changed=[])
    result = render_json5(diff)
    assert '\\"' in result
