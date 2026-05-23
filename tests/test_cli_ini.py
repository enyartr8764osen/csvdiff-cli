"""Tests for csvdiff.cli_ini."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_ini import handle_ini_output


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _diff_with_added() -> DiffResult:
    return DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_ini_output(_diff_with_added(), ["id", "name"], output_path=None)
    captured = capsys.readouterr()
    assert "[added]" in captured.out
    assert "name = Alice" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out = tmp_path / "result.ini"
    handle_ini_output(_diff_with_added(), ["id", "name"], output_path=str(out))
    content = out.read_text(encoding="utf-8")
    assert "[added]" in content
    assert "name = Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out = tmp_path / "sub" / "dir" / "result.ini"
    handle_ini_output(_empty_diff(), ["id"], output_path=str(out))
    assert out.exists()


def test_empty_diff_no_stdout_noise(capsys):
    handle_ini_output(_empty_diff(), ["id", "name"], output_path=None)
    captured = capsys.readouterr()
    # sections still emitted but no real row data
    assert "[added]" in captured.out
    assert "; (no rows)" in captured.out
