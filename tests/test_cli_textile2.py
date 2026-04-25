"""Tests for cli_textile2.handle_textile2_output."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_textile2 import handle_textile2_output


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
        unchanged=[],
    )


def _diff_with_added() -> DiffResult:
    diff = _empty_diff()
    diff.added.append({"id": "1", "name": "Alice"})
    return diff


def test_no_output_path_writes_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    handle_textile2_output(_diff_with_added(), None)
    captured = capsys.readouterr()
    assert "Alice" in captured.out


def test_output_path_writes_to_file(tmp_path: Path) -> None:
    out_file = tmp_path / "result.textile"
    handle_textile2_output(_diff_with_added(), str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path: Path) -> None:
    out_file = tmp_path / "nested" / "deep" / "result.textile"
    handle_textile2_output(_diff_with_added(), str(out_file))
    assert out_file.exists()


def test_no_changes_message_written_to_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    handle_textile2_output(_empty_diff(), None)
    captured = capsys.readouterr()
    assert "No differences" in captured.out
