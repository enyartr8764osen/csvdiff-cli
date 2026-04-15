"""Tests for csvdiff.render_xml."""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET

import pytest

from csvdiff.core import DiffResult
from csvdiff.render_xml import render_xml


def _empty_diff(**kwargs) -> DiffResult:
    defaults = dict(
        added=[],
        removed=[],
        changed=[],
        columns=["id", "name", "value"],
        key_columns=["id"],
    )
    defaults.update(kwargs)
    return DiffResult(**defaults)


def _parse(diff: DiffResult) -> ET.Element:
    buf = io.StringIO()
    render_xml(diff, buf)
    return ET.fromstring(buf.getvalue().split("\n", 1)[1])  # strip XML declaration


def test_root_element_is_csvdiff():
    root = _parse(_empty_diff())
    assert root.tag == "csvdiff"


def test_empty_diff_has_three_sections():
    root = _parse(_empty_diff())
    tags = [child.tag for child in root]
    assert tags == ["added", "removed", "changed"]


def test_added_row_appears_in_added_section():
    diff = _empty_diff(added=[{"id": "1", "name": "Alice", "value": "10"}])
    root = _parse(diff)
    added = root.find("added")
    assert added is not None
    rows = added.findall("row")
    assert len(rows) == 1
    fields = {f.get("name"): f.text for f in rows[0].findall("field")}
    assert fields["id"] == "1"
    assert fields["name"] == "Alice"


def test_removed_row_appears_in_removed_section():
    diff = _empty_diff(removed=[{"id": "2", "name": "Bob", "value": "20"}])
    root = _parse(diff)
    removed = root.find("removed")
    rows = removed.findall("row")
    assert len(rows) == 1
    fields = {f.get("name"): f.text for f in rows[0].findall("field")}
    assert fields["name"] == "Bob"


def test_changed_row_shows_old_and_new():
    old = {"id": "3", "name": "Carol", "value": "30"}
    new = {"id": "3", "name": "Carol", "value": "99"}
    diff = _empty_diff(changed=[("3",), old, new])
    # changed is list of tuples (key, old, new)
    diff2 = _empty_diff(changed=[(("3",), old, new)])
    root = _parse(diff2)
    changed = root.find("changed")
    changes = changed.findall("change")
    assert len(changes) == 1
    old_el = changes[0].find("old")
    new_el = changes[0].find("new")
    old_fields = {f.get("name"): f.text for f in old_el.findall("field")}
    new_fields = {f.get("name"): f.text for f in new_el.findall("field")}
    assert old_fields["value"] == "30"
    assert new_fields["value"] == "99"


def test_output_starts_with_xml_declaration():
    buf = io.StringIO()
    render_xml(_empty_diff(), buf)
    assert buf.getvalue().startswith('<?xml version="1.0" encoding="utf-8"?>')


def test_multiple_added_rows():
    rows = [
        {"id": str(i), "name": f"User{i}", "value": str(i * 10)}
        for i in range(1, 4)
    ]
    diff = _empty_diff(added=rows)
    root = _parse(diff)
    assert len(root.find("added").findall("row")) == 3
