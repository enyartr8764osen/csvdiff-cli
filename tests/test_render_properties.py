"""Tests for csvdiff.render_properties."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_properties import _escape_key, _escape_value, render_properties


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff: DiffResult, **kwargs) -> str:
    out = io.StringIO()
    render_properties(diff, out, **kwargs)
    return out.getvalue()


# --- escape helpers ---

def test_escape_value_plain_unchanged():
    assert _escape_value("hello") == "hello"


def test_escape_value_backslash():
    assert _escape_value("a\\b") == "a\\\\b"


def test_escape_value_newline():
    assert _escape_value("a\nb") == "a\\nb"


def test_escape_value_equals():
    assert _escape_value("a=b") == "a\\=b"


def test_escape_key_space():
    assert _escape_key("my key") == "my\\ key"


def test_escape_key_colon():
    assert _escape_key("a:b") == "a\\:b"


# --- render ---

def test_no_columns_returns_empty_string():
    diff = DiffResult(columns=[], added=[], removed=[], changed=[])
    assert _render(diff) == ""


def test_no_changes_produces_only_header_comment():
    result = _render(_empty_diff())
    assert result.startswith("# csvdiff output")
    # No section headers when nothing changed
    assert "# --- added" not in result
    assert "# --- removed" not in result
    assert "# --- changed" not in result


def test_added_row_appears_in_output():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = _render(diff)
    assert "# --- added ---" in result
    assert "added.0.id=1" in result
    assert "added.0.name=Alice" in result


def test_removed_row_appears_in_output():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = _render(diff)
    assert "# --- removed ---" in result
    assert "removed.0.id=2" in result
    assert "removed.0.name=Bob" in result


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[({"id": "3", "name": "Old"}, {"id": "3", "name": "New"})],
    )
    result = _render(diff)
    assert "# --- changed ---" in result
    assert "changed.0.old.name=Old" in result
    assert "changed.0.new.name=New" in result


def test_custom_columns_respected():
    diff = DiffResult(
        columns=["id", "name", "age"],
        added=[{"id": "1", "name": "Alice", "age": "30"}],
        removed=[],
        changed=[],
    )
    result = _render(diff, columns=["id", "name"])
    assert "added.0.id=1" in result
    assert "added.0.name=Alice" in result
    assert "age" not in result
