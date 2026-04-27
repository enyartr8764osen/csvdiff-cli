"""Render a DiffResult as KDL (KDL Document Language) output."""
from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult


def _escape(value: str) -> str:
    """Escape a string value for use inside a KDL quoted string."""
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    return value


def _quote(value: str) -> str:
    return f'"{_escape(value)}"'


def _row_to_node(row: dict[str, str], indent: str = "    ") -> str:
    """Render a single row dict as a KDL 'row' node with named properties."""
    props = " ".join(f"{k}={_quote(v)}" for k, v in row.items())
    return f"{indent}row {props}"


def _write_section(
    out: IO[str],
    name: str,
    rows: list[dict[str, str]],
) -> None:
    out.write(f"{name} {{\n")
    for row in rows:
        out.write(_row_to_node(row) + "\n")
    out.write("}\n")


def render_kdl(diff: DiffResult, out: IO[str]) -> None:
    """Write *diff* to *out* in KDL format.

    The document contains three top-level nodes: ``added``, ``removed``,
    and ``changed``.  Each node contains ``row`` child nodes whose
    columns are expressed as KDL properties.

    For changed rows the child nodes are named ``before`` and ``after``
    rather than ``row``.
    """
    if not diff.columns:
        return

    _write_section(out, "added", diff.added)
    _write_section(out, "removed", diff.removed)

    out.write("changed {\n")
    for old, new in diff.changed:
        out.write("    change {\n")
        props_old = " ".join(f"{k}={_quote(v)}" for k, v in old.items())
        props_new = " ".join(f"{k}={_quote(v)}" for k, v in new.items())
        out.write(f"        before {props_old}\n")
        out.write(f"        after {props_new}\n")
        out.write("    }\n")
    out.write("}\n")
