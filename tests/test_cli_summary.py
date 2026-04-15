"""Tests for csvdiff.cli_summary."""
from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_summary import handle_summary_output


def _empty_diff() -> DiffResult:
    return {"added": [], "removed": [], "changed": []}


def _diff_with_added() -> DiffResult:
    return {
        "added": [{"id": "1", "name": "Alice"}],
        "removed": [],
        "changed": [],
    }


def test_no_output_path_writes_to_stdout(capsys):
    handle_summary_output(_empty_diff(), None, color=False)
    captured = capsys.readouterr()
    assert "No differences found" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out_file = tmp_path / "summary.txt"
    handle_summary_output(_diff_with_added(), str(out_file), color=False)
    content = out_file.read_text(encoding="utf-8")
    assert "1 added" in content


def test_output_path_no_ansi_codes(tmp_path):
    out_file = tmp_path / "summary.txt"
    # Even if color=True is passed, file output should have no ANSI codes.
    handle_summary_output(_diff_with_added(), str(out_file), color=True)
    content = out_file.read_text(encoding="utf-8")
    assert "\033[" not in content


def test_stdout_color_flag_forwarded(capsys):
    handle_summary_output(_diff_with_added(), None, color=True)
    captured = capsys.readouterr()
    assert "\033[" in captured.out


def test_creates_file_in_nested_dir(tmp_path):
    nested = tmp_path / "reports"
    nested.mkdir()
    out_file = nested / "out.txt"
    handle_summary_output(_diff_with_added(), str(out_file))
    assert out_file.exists()
