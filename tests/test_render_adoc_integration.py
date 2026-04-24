"""Integration tests for render_adoc with realistic multi-row diffs."""
from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_adoc import render_adoc


def _make_diff(
    added=None,
    removed=None,
    changed=None,
    columns=None,
):
    return DiffResult(
        columns=columns or ["id", "name", "score"],
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def test_multiple_added_rows_all_appear():
    rows = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "85"},
    ]
    result = render_adoc(_make_diff(added=rows))
    assert "Alice" in result
    assert "Bob" in result


def test_multiple_removed_rows_all_appear():
    rows = [
        {"id": "3", "name": "Carol", "score": "70"},
        {"id": "4", "name": "Dave", "score": "60"},
    ]
    result = render_adoc(_make_diff(removed=rows))
    assert "Carol" in result
    assert "Dave" in result


def test_table_header_contains_all_columns():
    diff = _make_diff(added=[{"id": "1", "name": "Eve", "score": "95"}])
    result = render_adoc(diff)
    assert "id" in result
    assert "name" in result
    assert "score" in result


def test_output_is_valid_asciidoc_structure():
    diff = _make_diff(
        added=[{"id": "1", "name": "Frank", "score": "88"}],
        removed=[{"id": "2", "name": "Grace", "score": "77"}],
    )
    result = render_adoc(diff)
    # Title line
    assert result.startswith("=")
    # Table delimiters are balanced
    assert result.count("|===") % 2 == 0


def test_no_changes_each_section_has_no_rows_message():
    result = render_adoc(_make_diff())
    assert result.count("_No rows._") == 3
