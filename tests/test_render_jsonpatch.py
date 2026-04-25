"""Tests for csvdiff.render_jsonpatch."""
from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_jsonpatch import render_jsonpatch


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added={}, removed={}, changed={})


def _render(diff: DiffResult, *, pretty: bool = False) -> list[dict]:
    buf = io.StringIO()
    render_jsonpatch(diff, buf, pretty=pretty)
    return json.loads(buf.getvalue())


def test_no_changes_produces_empty_list() -> None:
    ops = _render(_empty_diff())
    assert ops == []


def test_added_row_produces_add_operation() -> None:
    diff = DiffResult(
        columns=["id", "name"],
        added={("1",): {"id": "1", "name": "Alice"}},
        removed={},
        changed={},
    )
    ops = _render(diff)
    assert len(ops) == 1
    op = ops[0]
    assert op["op"] == "add"
    assert op["path"].startswith("/added/")
    assert op["value"] == {"id": "1", "name": "Alice"}


def test_removed_row_produces_remove_operation() -> None:
    diff = DiffResult(
        columns=["id", "name"],
        added={},
        removed={("2",): {"id": "2", "name": "Bob"}},
        changed={},
    )
    ops = _render(diff)
    assert len(ops) == 1
    op = ops[0]
    assert op["op"] == "remove"
    assert op["path"].startswith("/removed/")
    assert op["value"] == {"id": "2", "name": "Bob"}


def test_changed_row_produces_replace_operation() -> None:
    diff = DiffResult(
        columns=["id", "name"],
        added={},
        removed={},
        changed={
            ("3",): ({"id": "3", "name": "Carol"}, {"id": "3", "name": "Caroline"})
        },
    )
    ops = _render(diff)
    assert len(ops) == 1
    op = ops[0]
    assert op["op"] == "replace"
    assert op["path"].startswith("/changed/")
    assert op["value"]["before"] == {"id": "3", "name": "Carol"}
    assert op["value"]["after"] == {"id": "3", "name": "Caroline"}


def test_path_segment_escapes_slash() -> None:
    diff = DiffResult(
        columns=["id"],
        added={("a/b",): {"id": "a/b"}},
        removed={},
        changed={},
    )
    ops = _render(diff)
    assert "~1" in ops[0]["path"]


def test_path_segment_escapes_tilde() -> None:
    diff = DiffResult(
        columns=["id"],
        added={("a~b",): {"id": "a~b"}},
        removed={},
        changed={},
    )
    ops = _render(diff)
    assert "~0" in ops[0]["path"]


def test_pretty_flag_produces_indented_output() -> None:
    diff = DiffResult(
        columns=["id"],
        added={("1",): {"id": "1"}},
        removed={},
        changed={},
    )
    buf = io.StringIO()
    render_jsonpatch(diff, buf, pretty=True)
    text = buf.getvalue()
    assert "\n  " in text


def test_output_ends_with_newline() -> None:
    buf = io.StringIO()
    render_jsonpatch(_empty_diff(), buf)
    assert buf.getvalue().endswith("\n")
