"""Tests for cli_confluence handler."""
import pytest
from io import StringIO
from csvdiff.core import DiffResult
from csvdiff.cli_confluence import handle_confluence_output, _render_to_stream


def _empty_diff():
    return DiffResult(columns=["id", "val"], added=[], removed=[], changed=[])


def _diff_with_added():
    return DiffResult(
        columns=["id", "val"],
        added=[{"id": "1", "val": "x"}],
        removed=[],
        changed=[],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_confluence_output(_diff_with_added(), None)
    captured = capsys.readouterr()
    assert "Added Rows" in captured.out


def test_output_path_writes_to_file(tmp_path):
    out_file = tmp_path / "out.txt"
    handle_confluence_output(_diff_with_added(), str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "Added Rows" in content


def test_output_path_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "sub" / "dir" / "out.txt"
    handle_confluence_output(_diff_with_added(), str(out_file))
    assert out_file.exists()


def test_empty_diff_still_writes_headers(tmp_path):
    out_file = tmp_path / "out.txt"
    handle_confluence_output(_empty_diff(), str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "h3." in content
