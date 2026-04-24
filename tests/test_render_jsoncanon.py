"""Tests for csvdiff.render_jsoncanon."""

from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsoncanon import render_jsoncanon


def _empty_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, changed={})


def _render(diff: DiffResult, key_columns=None, indent=2) -> dict:
    buf = io.StringIO()
    render_jsoncanon(diff, buf, key_columns=key_columns or [], indent=indent)
    return json.loads(buf.getvalue())


def test_empty_diff_has_three_sections():
    result = _render(_empty_diff())
    assert set(result.keys()) == {"added", "removed", "changed"}


def test_empty_diff_all_sections_are_lists():
    result = _render(_empty_diff())
    assert result["added"] == []
    assert result["removed"] == []
    assert result["changed"] == []


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        added={("alice",): {"name": "alice", "score": "10"}},
        removed={},
        changed={},
    )
    result = _render(diff, key_columns=["name"])
    assert len(result["added"]) == 1
    entry = result["added"][0]
    assert entry["row"] == {"name": "alice", "score": "10"}
    assert entry["key"] == {"name": "alice"}


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        added={},
        removed={("bob",): {"name": "bob", "score": "20"}},
        changed={},
    )
    result = _render(diff, key_columns=["name"])
    assert len(result["removed"]) == 1
    assert result["removed"][0]["row"]["name"] == "bob"


def test_changed_row_has_old_and_new():
    diff = DiffResult(
        added={},
        removed={},
        changed={
            ("carol",): (
                {"name": "carol", "score": "5"},
                {"name": "carol", "score": "15"},
            )
        },
    )
    result = _render(diff, key_columns=["name"])
    assert len(result["changed"]) == 1
    entry = result["changed"][0]
    assert entry["old"]["score"] == "5"
    assert entry["new"]["score"] == "15"


def test_row_keys_are_sorted():
    diff = DiffResult(
        added={("z",): {"z_col": "z", "a_col": "a", "m_col": "m"}},
        removed={},
        changed={},
    )
    result = _render(diff, key_columns=["z_col"])
    row_keys = list(result["added"][0]["row"].keys())
    assert row_keys == sorted(row_keys)


def test_top_level_keys_are_sorted():
    result = _render(_empty_diff())
    keys = list(result.keys())
    assert keys == sorted(keys)


def test_compact_indent_produces_single_line_output():
    buf = io.StringIO()
    render_jsoncanon(_empty_diff(), buf, key_columns=[], indent=None)
    output = buf.getvalue().strip()
    assert "\n" not in output


def test_output_ends_with_newline():
    buf = io.StringIO()
    render_jsoncanon(_empty_diff(), buf, key_columns=[])
    assert buf.getvalue().endswith("\n")
