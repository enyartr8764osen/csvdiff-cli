"""Tests for csvdiff.cli_adoc."""
from __future__ import annotations

import io
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_adoc import handle_adoc_output


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
    handle_adoc_output(_diff_with_added(), output_path=None)
    captured = capsys.readouterr()
    assert "Alice" in captured.out


def test_no_output_path_includes_title(capsys):
    handle_adoc_output(_empty_diff(), output_path=None, title="Test Title")
    captured = capsys.readouterr()
    assert "= Test Title" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out_file = tmp_path / "diff.adoc"
    handle_adoc_output(_diff_with_added(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "nested" / "dir" / "diff.adoc"
    handle_adoc_output(_empty_diff(), output_path=str(out_file))
    assert out_file.exists()


def test_output_file_contains_section_headers(tmp_path):
    out_file = tmp_path / "diff.adoc"
    handle_adoc_output(_empty_diff(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "== Added Rows" in content
    assert "== Removed Rows" in content
    assert "== Changed Rows" in content
