"""Tests for csvdiff.cli_mediawiki."""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_mediawiki import handle_mediawiki_output, _render_to_stream


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def _diff_with_added() -> DiffResult:
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    return diff


def test_no_output_path_writes_to_stdout(capsys):
    handle_mediawiki_output(_empty_diff(), output_path=None)
    captured = capsys.readouterr()
    assert "No differences found." in captured.out


def test_output_path_writes_to_file(tmp_path):
    out_file = tmp_path / "diff.mediawiki"
    handle_mediawiki_output(_diff_with_added(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "Added Rows" in content
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "nested" / "dir" / "diff.mediawiki"
    handle_mediawiki_output(_diff_with_added(), output_path=str(out_file))
    assert out_file.exists()


def test_render_to_stream_no_changes():
    buf = io.StringIO()
    _render_to_stream(_empty_diff(), buf)
    assert "No differences found." in buf.getvalue()


def test_render_to_stream_with_changes():
    buf = io.StringIO()
    _render_to_stream(_diff_with_added(), buf)
    result = buf.getvalue()
    assert "wikitable" in result
    assert "Alice" in result
