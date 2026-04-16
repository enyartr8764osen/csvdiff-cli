"""Tests for render_textile."""
from csvdiff.core import DiffResult
from csvdiff.render_textile import render_textile


def _empty_diff():
    return DiffResult(columns=["id", "name"], added=[], removed=[], changed=[])


def test_no_changes_produces_empty_string():
    assert render_textile(_empty_diff()) == ""


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = render_textile(diff)
    assert "h2. Added" in out
    assert "Alice" in out
    assert "h2. Removed" not in out


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    out = render_textile(diff)
    assert "h2. Removed" in out
    assert "Bob" in out


def test_changed_row_shows_before_and_after():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[({"id": "3", "name": "Old"}, {"id": "3", "name": "New"})],
    )
    out = render_textile(diff)
    assert "h2. Changed" in out
    assert "Before" in out
    assert "After" in out
    assert "Old" in out
    assert "New" in out


def test_table_rows_use_pipe_syntax():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = render_textile(diff)
    lines = [l for l in out.splitlines() if l.startswith("|")]
    assert len(lines) >= 2  # header + data row


def test_header_uses_textile_header_syntax():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    out = render_textile(diff)
    assert "_.id" in out
    assert "_.name" in out
