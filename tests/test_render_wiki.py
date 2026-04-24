"""Tests for csvdiff.render_wiki."""
from csvdiff.core import DiffResult
from csvdiff.render_wiki import render_wiki


def _empty_diff(columns=None):
    return DiffResult(
        columns=columns or ["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def test_no_columns_returns_empty_string():
    diff = _empty_diff(columns=[])
    assert render_wiki(diff) == ""


def test_no_changes_produces_no_rows_messages():
    result = render_wiki(_empty_diff())
    assert "(no rows)" in result


def test_section_headers_present():
    result = render_wiki(_empty_diff())
    assert "== Added Rows ==" in result
    assert "== Removed Rows ==" in result
    assert "== Changed Rows (before) ==" in result
    assert "== Changed Rows (after) ==" in result


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_wiki(diff)
    assert "Alice" in result
    added_section = result.split("== Added Rows ==")[1].split("==")[0]
    assert "Alice" in added_section


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    result = render_wiki(diff)
    removed_section = result.split("== Removed Rows ==")[1].split("==")[0]
    assert "Bob" in removed_section


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[{"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}],
    )
    result = render_wiki(diff)
    before_section = result.split("== Changed Rows (before) ==")[1].split("==")[0]
    after_section = result.split("== Changed Rows (after) ==")[1].split("==")[0]
    assert "Carol" in before_section
    assert "Caroline" in after_section


def test_table_rows_use_pipe_syntax():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    result = render_wiki(diff)
    lines = [l for l in result.splitlines() if "Alice" in l]
    assert lines, "Expected at least one line containing 'Alice'"
    assert lines[0].startswith("||")
    assert lines[0].endswith("||")


def test_header_row_contains_column_names():
    diff = DiffResult(
        columns=["id", "value"],
        added=[{"id": "10", "value": "x"}],
        removed=[],
        changed=[],
    )
    result = render_wiki(diff)
    added_block = result.split("== Added Rows ==")[1].split("\n\n")[0]
    assert "id" in added_block
    assert "value" in added_block
