"""Tests for csvdiff.render_toml."""
from __future__ import annotations

from csvdiff.core import DiffResult
from csvdiff.render_toml import render_toml


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _parse_toml_list(block: str) -> list[dict]:
    """Very small TOML inline-table list parser for test assertions."""
    import re

    rows: list[dict] = []
    for match in re.finditer(r"\{([^}]*)\}", block):
        inner = match.group(1)
        row: dict[str, str] = {}
        for pair in re.finditer(r'(\w+)\s*=\s*"((?:[^\\"]|\\.)*)"', inner):
            row[pair.group(1)] = pair.group(2)
        rows.append(row)
    return rows


def test_no_changes_produces_empty_sections():
    output = render_toml(_empty_diff())
    assert "added = []" in output
    assert "removed = []" in output
    assert "changed = []" in output


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    output = render_toml(diff)
    assert "added = [" in output
    rows = _parse_toml_list(output.split("removed")[0])
    assert any(r.get("id") == "1" and r.get("name") == "Alice" for r in rows)


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    output = render_toml(diff)
    assert "removed = [" in output
    removed_block = output.split("removed")[1].split("changed")[0]
    rows = _parse_toml_list(removed_block)
    assert any(r.get("id") == "2" and r.get("name") == "Bob" for r in rows)


def test_changed_row_shows_old_and_new():
    diff = DiffResult(
        added=[],
        removed=[],
        changed=[(
            {"id": "3", "name": "Carol"},
            {"id": "3", "name": "Caroline"},
        )],
    )
    output = render_toml(diff)
    assert "changed = [" in output
    assert "old =" in output
    assert "new =" in output
    assert "Carol" in output
    assert "Caroline" in output


def test_special_characters_are_escaped():
    diff = DiffResult(
        added=[{"id": "4", "note": 'say "hello"'}],
        removed=[],
        changed=[],
    )
    output = render_toml(diff)
    assert '\\"hello\\"' in output


def test_output_ends_with_newline():
    output = render_toml(_empty_diff())
    assert output.endswith("\n")
