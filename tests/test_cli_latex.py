"""Tests for csvdiff.cli_latex."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_latex import handle_latex_output


def _empty_diff() -> DiffResult:
    return DiffResult(
        columns=["id", "value"],
        added=[],
        removed=[],
        changed=[],
    )


def _diff_with_added() -> DiffResult:
    d = _empty_diff()
    d.added.append({"id": "1", "value": "alpha"})
    return d


# ---------------------------------------------------------------------------
# stdout path
# ---------------------------------------------------------------------------

def test_no_output_path_writes_to_stdout(capsys):
    handle_latex_output(_empty_diff(), None)
    captured = capsys.readouterr()
    assert "csvdiff-cli" in captured.out


def test_no_output_path_includes_preamble(capsys):
    handle_latex_output(_empty_diff(), None)
    captured = capsys.readouterr()
    assert r"\usepackage{xcolor}" in captured.out
    assert r"\usepackage{longtable}" in captured.out


def test_no_preamble_flag_omits_usepackage(capsys):
    handle_latex_output(_empty_diff(), None, preamble=False)
    captured = capsys.readouterr()
    assert r"\usepackage" not in captured.out


# ---------------------------------------------------------------------------
# file output path
# ---------------------------------------------------------------------------

def test_output_path_writes_file(tmp_path):
    out_file = tmp_path / "diff.tex"
    handle_latex_output(_diff_with_added(), str(out_file))
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "alpha" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "nested" / "dir" / "diff.tex"
    handle_latex_output(_empty_diff(), str(out_file))
    assert out_file.exists()


def test_output_file_contains_preamble(tmp_path):
    out_file = tmp_path / "out.tex"
    handle_latex_output(_empty_diff(), str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert r"\usepackage{longtable}" in content


def test_output_file_no_preamble(tmp_path):
    out_file = tmp_path / "out.tex"
    handle_latex_output(_empty_diff(), str(out_file), preamble=False)
    content = out_file.read_text(encoding="utf-8")
    assert r"\usepackage" not in content
