"""Tests for csvdiff.render_plist."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_plist import render_plist


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _parse(text: str) -> ET.Element:
    """Parse plist XML, skipping the DOCTYPE declaration."""
    lines = [l for l in text.splitlines() if not l.startswith("<!")]
    return ET.fromstring("\n".join(lines))


def test_output_starts_with_xml_declaration():
    out = render_plist(_empty_diff())
    assert out.startswith("<?xml version=\"1.0\"")


def test_root_element_is_plist():
    root = _parse(render_plist(_empty_diff()))
    assert root.tag == "plist"


def test_plist_version_attribute():
    root = _parse(render_plist(_empty_diff()))
    assert root.attrib.get("version") == "1.0"


def test_empty_diff_has_three_sections():
    root = _parse(render_plist(_empty_diff()))
    d = root.find("dict")
    keys = [el.text for el in d if el.tag == "key"]
    assert keys == ["added", "removed", "changed"]


def test_empty_sections_are_empty_arrays():
    root = _parse(render_plist(_empty_diff()))
    d = root.find("dict")
    arrays = [el for el in d if el.tag == "array"]
    assert all(len(arr) == 0 for arr in arrays)


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    root = _parse(render_plist(diff))
    d = root.find("dict")
    children = list(d)
    # added key is first, its array is second child
    added_array = children[1]
    assert added_array.tag == "array"
    assert len(added_array) == 1
    row_dict = added_array[0]
    keys = [el.text for el in row_dict if el.tag == "key"]
    values = [el.text for el in row_dict if el.tag == "string"]
    assert "id" in keys
    assert "name" in keys
    assert "Alice" in values


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    root = _parse(render_plist(diff))
    d = root.find("dict")
    children = list(d)
    removed_array = children[3]  # key, array, key, array ...
    assert removed_array.tag == "array"
    assert len(removed_array) == 1
    values = [el.text for el in removed_array[0] if el.tag == "string"]
    assert "Bob" in values


def test_changed_row_appears_in_changed_section():
    diff = DiffResult(
        added=[],
        removed=[],
        changed=[
            {"old": {"id": "3", "name": "Carol"}, "new": {"id": "3", "name": "Caroline"}}
        ],
    )
    out = render_plist(diff)
    assert "Caroline" in out
    assert "Carol" in out
    root = _parse(out)
    d = root.find("dict")
    children = list(d)
    changed_array = children[5]
    assert changed_array.tag == "array"
    assert len(changed_array) == 1
