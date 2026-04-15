"""Render a DiffResult as an XML document."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import IO

from csvdiff.core import DiffResult


def _row_to_element(tag: str, row: dict[str, str]) -> ET.Element:
    """Create an XML element with child <field> elements for each column."""
    elem = ET.Element(tag)
    for col, val in row.items():
        field = ET.SubElement(elem, "field", name=col)
        field.text = val
    return elem


def _indent(elem: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation in-place (stdlib ET has no built-in indent pre-3.9)."""
    indent = "\n" + "  " * level
    if len(elem):
        elem.text = indent + "  "
        for child in elem:
            _indent(child, level + 1)
            child.tail = indent + "  "
        elem[-1].tail = indent
    else:
        elem.text = elem.text or ""
    elem.tail = "\n" if level == 0 else indent


def render_xml(diff: DiffResult, stream: IO[str]) -> None:
    """Write an XML representation of *diff* to *stream*."""
    root = ET.Element("csvdiff")

    added_el = ET.SubElement(root, "added")
    for row in diff.added:
        added_el.append(_row_to_element("row", row))

    removed_el = ET.SubElement(root, "removed")
    for row in diff.removed:
        removed_el.append(_row_to_element("row", row))

    changed_el = ET.SubElement(root, "changed")
    for key, old, new in diff.changed:
        change = ET.SubElement(changed_el, "change")
        key_el = ET.SubElement(change, "key")
        for k, v in zip(diff.key_columns, key):
            kf = ET.SubElement(key_el, "field", name=k)
            kf.text = v
        change.append(_row_to_element("old", old))
        change.append(_row_to_element("new", new))

    _indent(root)
    tree = ET.ElementTree(root)
    stream.write('<?xml version="1.0" encoding="utf-8"?>\n')
    ET.indent(tree.getroot()) if hasattr(ET, "indent") else None
    stream.write(ET.tostring(root, encoding="unicode"))
    stream.write("\n")
