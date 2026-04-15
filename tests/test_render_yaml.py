"""Tests for csvdiff.render_yaml."""
from __future__ import annotations

import io

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_yaml import render_yaml


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _render(diff: DiffResult) -> str:
    buf = io.StringIO()
    render_yaml(diff, buf)
    return buf.getvalue()


def test_output_starts_with_yaml_document_marker():
    out = _render(_empty_diff())
    assert out.startswith("---\n")


def test_empty_diff_has_three_sections():
    out = _render(_empty_diff())
    assert "added:" in out
    assert "removed:" in out
    assert "changed:" in out


def test_empty_sections_use_empty_list_literal():
    out = _render(_empty_diff())
    assert out.count("    []\n") == 3


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert "added:" in out
    assert "id: 1" in out
    assert "name: Alice" in out


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    out = _render(diff)
    assert "removed:" in out
    assert "id: 2" in out
    assert "name: Bob" in out


def test_changed_row_shows_old_and_new():
    old = {"id": "3", "name": "Carol"}
    new = {"id": "3", "name": "Caroline"}
    diff = DiffResult(added=[], removed=[], changed=[(old, new)])
    out = _render(diff)
    assert "changed:" in out
    assert "old:" in out
    assert "new:" in out
    assert "Carol" in out
    assert "Caroline" in out


def test_value_with_colon_is_quoted():
    diff = DiffResult(
        added=[{"id": "1", "label": "foo: bar"}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert '"foo: bar"' in out


def test_empty_value_is_quoted():
    diff = DiffResult(
        added=[{"id": "1", "note": ""}],
        removed=[],
        changed=[],
    )
    out = _render(diff)
    assert 'note: ""' in out
