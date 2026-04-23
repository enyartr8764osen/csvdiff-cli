"""Tests for csvdiff.cli_rtf."""

from __future__ import annotations

import io
import pathlib

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_rtf import handle_rtf_output


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _diff_with_added() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_rtf_output(_empty_diff(), output_path=None)
    captured = capsys.readouterr()
    assert "{\\rtf1" in captured.out


def test_output_path_writes_to_file(tmp_path):
    dest = tmp_path / "out.rtf"
    handle_rtf_output(_diff_with_added(), output_path=str(dest))
    content = dest.read_text(encoding="utf-8")
    assert "{\\rtf1" in content
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "deep" / "out.rtf"
    handle_rtf_output(_empty_diff(), output_path=str(dest))
    assert dest.exists()


def test_output_file_is_valid_rtf_structure(tmp_path):
    dest = tmp_path / "result.rtf"
    handle_rtf_output(_diff_with_added(), output_path=str(dest))
    content = dest.read_text(encoding="utf-8")
    assert content.strip().endswith("}")
