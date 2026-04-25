"""Tests for csvdiff.cli_mustache."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_mustache import handle_mustache_output


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def _diff_with_added():
    return DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_mustache_output(_diff_with_added(), output_path=None)
    captured = capsys.readouterr()
    assert "{{#added}}" in captured.out
    assert "Alice" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out_file = tmp_path / "result.mustache"
    handle_mustache_output(_diff_with_added(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "{{#added}}" in content
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "nested" / "dir" / "result.txt"
    handle_mustache_output(_empty_diff(), output_path=str(out_file))
    assert out_file.exists()


def test_empty_diff_still_writes_sections(tmp_path):
    out_file = tmp_path / "empty.txt"
    handle_mustache_output(_empty_diff(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "{{#added}}" in content
    assert "{{#removed}}" in content
    assert "{{#changed}}" in content
