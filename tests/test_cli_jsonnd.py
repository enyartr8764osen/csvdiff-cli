"""Tests for csvdiff.cli_jsonnd."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_jsonnd import handle_jsonnd_output


def _empty_diff() -> DiffResult:
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def _diff_with_added() -> DiffResult:
    return DiffResult(
        columns=["id", "name"],
        added=[(("1",), ("1", "Alice"))],
        removed=[],
        changed=[],
    )


# ---------------------------------------------------------------------------
# stdout path
# ---------------------------------------------------------------------------

def test_no_output_path_writes_to_stdout(capsys):
    handle_jsonnd_output(_diff_with_added(), None, key_columns=["id"])
    out = capsys.readouterr().out
    assert out.strip() != ""
    record = json.loads(out.strip().splitlines()[0])
    assert record["status"] == "added"


def test_empty_diff_produces_no_stdout_output(capsys):
    handle_jsonnd_output(_empty_diff(), None, key_columns=["id"])
    out = capsys.readouterr().out
    assert out.strip() == ""


# ---------------------------------------------------------------------------
# file path
# ---------------------------------------------------------------------------

def test_output_path_writes_to_file(tmp_path):
    dest = tmp_path / "out.jsonnd"
    handle_jsonnd_output(_diff_with_added(), str(dest), key_columns=["id"])
    assert dest.exists()
    lines = dest.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["status"] == "added"


def test_output_path_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "dir" / "out.jsonnd"
    handle_jsonnd_output(_diff_with_added(), str(dest), key_columns=["id"])
    assert dest.exists()


def test_output_path_empty_diff_writes_empty_file(tmp_path):
    dest = tmp_path / "empty.jsonnd"
    handle_jsonnd_output(_empty_diff(), str(dest), key_columns=["id"])
    assert dest.read_text(encoding="utf-8").strip() == ""
