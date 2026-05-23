"""Tests for csvdiff.cli_dot."""
from __future__ import annotations

import io
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_dot import handle_dot_output


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
    handle_dot_output(_diff_with_added(), None)
    captured = capsys.readouterr()
    assert "graph" in captured.out
    assert "Alice" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out = tmp_path / "result.dot"
    handle_dot_output(_diff_with_added(), str(out))
    content = out.read_text(encoding="utf-8")
    assert "graph" in content
    assert "Alice" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out = tmp_path / "subdir" / "nested" / "result.dot"
    handle_dot_output(_diff_with_added(), str(out))
    assert out.exists()


def test_no_preamble_flag_omits_graph_declaration(capsys):
    handle_dot_output(_empty_diff(), None, no_preamble=True)
    captured = capsys.readouterr()
    assert not captured.out.strip().startswith("graph ")


def test_custom_graph_name_in_output(capsys):
    handle_dot_output(_empty_diff(), None, graph_name="testgraph")
    captured = capsys.readouterr()
    assert "testgraph" in captured.out
