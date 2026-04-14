"""Tests for csvdiff.filters module."""

import pytest
from csvdiff.filters import (
    filter_columns,
    filter_rows_by_column,
    normalize_whitespace,
)

SAMPLE = [
    {"id": "1", "name": "Alice", "dept": "eng"},
    {"id": "2", "name": "Bob", "dept": "hr"},
    {"id": "3", "name": "Carol", "dept": "eng"},
]


def test_filter_columns_include():
    result = filter_columns(SAMPLE, include=["id", "name"])
    assert result == [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}, {"id": "3", "name": "Carol"}]


def test_filter_columns_exclude():
    result = filter_columns(SAMPLE, exclude=["dept"])
    assert all("dept" not in row for row in result)
    assert all("id" in row and "name" in row for row in result)


def test_filter_columns_both_raises():
    with pytest.raises(ValueError, match="not both"):
        filter_columns(SAMPLE, include=["id"], exclude=["dept"])


def test_filter_columns_missing_column_raises():
    with pytest.raises(ValueError, match="not found"):
        filter_columns(SAMPLE, include=["id", "nonexistent"])


def test_filter_columns_empty_rows():
    assert filter_columns([], include=["id"n
def test_filter__filter():
    result = filter_columns(SAMPLE)
    assert result == SAMPLE


def test_filter_rows_by_column():
    result = filter_rows_by_column(SAMPLE, "dept", "eng")
    assert len(result) == 2
    assert all(row["dept"] == "eng" for row in result)


def test_filter_rows_by_column_no_match():
    result = filter_rows_by_column(SAMPLE, "dept", "finance")
    assert result == []


def test_filter_rows_by_column_missing_column_raises():
    with pytest.raises(ValueError, match="not found"):
        filter_rows_by_column(SAMPLE, "salary", "100")


def test_normalize_whitespace():
    dirty = [{"id": " 1 ", "name": "  Alice", "dept": "eng "}]
    result = normalize_whitespace(dirty)
    assert result == [{"id": "1", "name": "Alice", "dept": "eng"}]


def test_normalize_whitespace_non_string_values():
    rows = [{"id": 1, "value": 3.14}]
    result = normalize_whitespace(rows)
    assert result == [{"id": 1, "value": 3.14}]
