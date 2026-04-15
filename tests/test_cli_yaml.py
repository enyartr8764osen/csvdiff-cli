"""Tests for csvdiff.cli_yaml."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_yaml import handle_yaml_output


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _diff_with_added() -> DiffResult:
    return DiffResult(
        added=[{"id": "10", "name": "Zara"}],
        removed=[],
        changed=[],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_yaml_output(_diff_with_added(), output_path=None)
    captured = capsys.readouterr()
    assert "added:" in captured.out
    assert "Zara" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out_file = tmp_path / "diff.yaml"
    handle_yaml_output(_diff_with_added(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "---" in content
    assert "Zara" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "sub" / "dir" / "diff.yaml"
    handle_yaml_output(_empty_diff(), output_path=str(out_file))
    assert out_file.exists()


def test_empty_diff_written_to_file(tmp_path):
    out_file = tmp_path / "empty.yaml"
    handle_yaml_output(_empty_diff(), output_path=str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert content.count("    []\n") == 3
