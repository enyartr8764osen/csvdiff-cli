"""Tests for csvdiff.cli_s3v."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_s3v import handle_s3v_output


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def _diff_with_added() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_s3v_output(_diff_with_added(), None)
    captured = capsys.readouterr()
    assert "(csvdiff" in captured.out


def test_output_path_writes_to_file(tmp_path):
    dest = tmp_path / "out.sexp"
    handle_s3v_output(_diff_with_added(), str(dest))
    content = dest.read_text(encoding="utf-8")
    assert "(csvdiff" in content
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "dir" / "out.sexp"
    handle_s3v_output(_diff_with_added(), str(dest))
    assert dest.exists()


def test_empty_diff_file_has_three_sections(tmp_path):
    dest = tmp_path / "empty.sexp"
    handle_s3v_output(_empty_diff(), str(dest))
    content = dest.read_text(encoding="utf-8")
    assert "(added" in content
    assert "(removed" in content
    assert "(changed" in content
