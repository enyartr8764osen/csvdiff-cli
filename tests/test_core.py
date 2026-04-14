"""Tests for csvdiff.core module."""

import os
import tempfile
import pytest
from csvdiff.core import diff_csvs, load_csv, DiffResult


def write_csv(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_no_changes(tmp_dir):
    content = "id,name,value\n1,Alice,100\n2,Bob,200\n"
    old = os.path.join(tmp_dir, "old.csv")
    new = os.path.join(tmp_dir, "new.csv")
    write_csv(old, content)
    write_csv(new, content)
    result = diff_csvs(old, new, key_columns=["id"])
    assert not result.has_changes


def test_added_row(tmp_dir):
    old = os.path.join(tmp_dir, "old.csv")
    new = os.path.join(tmp_dir, "new.csv")
    write_csv(old, "id,name\n1,Alice\n")
    write_csv(new, "id,name\n1,Alice\n2,Bob\n")
    result = diff_csvs(old, new, key_columns=["id"])
    assert len(result.added) == 1
    assert result.added[0]["name"] == "Bob"
    assert result.removed == []
    assert result.modified == []


def test_removed_row(tmp_dir):
    old = os.path.join(tmp_dir, "old.csv")
    new = os.path.join(tmp_dir, "new.csv")
    write_csv(old, "id,name\n1,Alice\n2,Bob\n")
    write_csv(new, "id,name\n1,Alice\n")
    result = diff_csvs(old, new, key_columns=["id"])
    assert len(result.removed) == 1
    assert result.removed[0]["id"] == "2"


def test_modified_row(tmp_dir):
    old = os.path.join(tmp_dir, "old.csv")
    new = os.path.join(tmp_dir, "new.csv")
    write_csv(old, "id,name\n1,Alice\n")
    write_csv(new, "id,name\n1,Alicia\n")
    result = diff_csvs(old, new, key_columns=["id"])
    assert len(result.modified) == 1
    old_row, new_row = result.modified[0]
    assert old_row["name"] == "Alice"
    assert new_row["name"] == "Alicia"


def test_invalid_key_column(tmp_dir):
    content = "id,name\n1,Alice\n"
    old = os.path.join(tmp_dir, "old.csv")
    new = os.path.join(tmp_dir, "new.csv")
    write_csv(old, content)
    write_csv(new, content)
    with pytest.raises(ValueError, match="Key columns not found"):
        diff_csvs(old, new, key_columns=["nonexistent"])


def test_summary_string(tmp_dir):
    old = os.path.join(tmp_dir, "old.csv")
    new = os.path.join(tmp_dir, "new.csv")
    write_csv(old, "id,name\n1,Alice\n2,Bob\n")
    write_csv(new, "id,name\n2,Bobby\n3,Carol\n")
    result = diff_csvs(old, new, key_columns=["id"])
    assert "Added: 1" in result.summary
    assert "Removed: 1" in result.summary
    assert "Modified: 1" in result.summary
