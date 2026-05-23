"""Render a DiffResult as an Apple Property List (XML plist)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from io import StringIO
from typing import List, Dict

from csvdiff.core import DiffResult


def _row_to_dict_element(row: Dict[str, str]) -> ET.Element:
    """Convert a row dict to a plist <dict> element."""
    d = ET.Element("dict")
    for key, value in row.items():
        k_el = ET.SubElement(d, "key")
        k_el.text = key
        v_el = ET.SubElement(d, "string")
        v_el.text = value
    return d


def _write_section(parent: ET.Element, label: str, rows: List[Dict[str, str]]) -> None:
    """Write a labelled array section into a plist dict element."""
    k = ET.SubElement(parent, "key")
    k.text = label
    arr = ET.SubElement(parent, "array")
    for row in rows:
        arr.append(_row_to_dict_element(row))


def _indent(elem: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation in-place."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def render_plist(diff: DiffResult) -> str:
    """Return a plist XML string representing *diff*."""
    plist = ET.Element("plist", version="1.0")
    root_dict = ET.SubElement(plist, "dict")

    _write_section(root_dict, "added", diff.added)
    _write_section(root_dict, "removed", diff.removed)
    _write_section(root_dict, "changed", [
        {"old_" + k: v for k, v in entry["old"].items()} |
        {"new_" + k: v for k, v in entry["new"].items()}
        for entry in diff.changed
    ])

    _indent(plist)
    tree = ET.ElementTree(plist)
    buf = StringIO()
    buf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    buf.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"\n')
    buf.write('  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
    ET.indent(plist, space="  ")
    buf.write(ET.tostring(plist, encoding="unicode"))
    buf.write("\n")
    return buf.getvalue()
