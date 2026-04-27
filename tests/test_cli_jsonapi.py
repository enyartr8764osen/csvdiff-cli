"""Tests for csvdiff.cli_jsonapi."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from csvdiff.core import DiffResult
from csvdiff.cli_jsonapi import handle_jsonapi_output


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[], columns=[])


def _diff_with_added() -> DiffResult:
    return DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
        columns=["id", "name"],
    )


def test_no_output_path_writes_to_stdout(capsys):
    handle_jsonapi_output(_empty_diff(), output=None)
    captured = capsys.readouterr()
    doc = json.loads(captured.out)
    assert "data" in doc
    assert "meta" in doc


def test_output_path_writes_to_file(tmp_path):
    dest = tmp_path / "out.json"
    handle_jsonapi_output(_diff_with_added(), output=str(dest))
    assert dest.exists()
    doc = json.loads(dest.read_text())
    assert doc["meta"]["added"] == 1


def test_output_path_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "dir" / "out.json"
    handle_jsonapi_output(_empty_diff(), output=str(dest))
    assert dest.exists()


def test_custom_indent_is_respected(tmp_path):
    dest = tmp_path / "out.json"
    handle_jsonapi_output(_empty_diff(), output=str(dest), indent=4)
    raw = dest.read_text()
    # 4-space indent means lines start with four spaces
    assert "    " in raw
