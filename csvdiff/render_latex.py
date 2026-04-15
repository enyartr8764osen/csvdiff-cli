"""Render a DiffResult as a LaTeX longtable document fragment."""
from __future__ import annotations

from typing import IO

from csvdiff.core import DiffResult, has_changes


def _escape(text: str) -> str:
    """Escape special LaTeX characters in a string."""
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("\\", r"\textbackslash{}"),
    ]
    for char, replacement in replacements:
        text = text.replace(char, replacement)
    return text


def _row_to_cells(row: dict[str, str]) -> str:
    """Convert a row dict to a LaTeX table row string."""
    return " & ".join(_escape(v) for v in row.values()) + r" \\"


def _render_section(
    out: IO[str],
    title: str,
    color: str,
    rows: list[dict[str, str]],
    columns: list[str],
) -> None:
    if not rows:
        return
    col_spec = "|".join(["l"] * len(columns))
    header = " & ".join(r"\textbf{" + _escape(c) + "}" for c in columns)
    out.write(f"\\subsection*{{{title}}}\n")
    out.write(f"\\begin{{longtable}}{{|{col_spec}|}}\n")
    out.write("\\hline\n")
    out.write(header + r" \\" + "\n")
    out.write("\\hline\n")
    for row in rows:
        out.write(f"{{\\color{{{color}}} {_row_to_cells(row)}}}\n")
    out.write("\\hline\n")
    out.write("\\end{longtable}\n")


def render_latex(diff: DiffResult, out: IO[str]) -> None:
    """Write LaTeX output for *diff* to *out*."""
    if not has_changes(diff):
        out.write("% No differences found.\n")
        return

    columns = diff.columns

    _render_section(out, "Added Rows", "green", diff.added, columns)
    _render_section(out, "Removed Rows", "red", diff.removed, columns)

    if diff.changed:
        out.write("\\subsection*{Changed Rows}\n")
        for old, new in diff.changed:
            col_spec = "|".join(["l"] * len(columns))
            header = " & ".join(r"\textbf{" + _escape(c) + "}" for c in columns)
            out.write(f"\\begin{{longtable}}{{|{col_spec}|}}\n")
            out.write("\\hline\n")
            out.write(header + r" \\" + "\n")
            out.write("\\hline\n")
            out.write(f"{{\\color{{red}} {_row_to_cells(old)}}}\n")
            out.write(f"{{\\color{{blue}} {_row_to_cells(new)}}}\n")
            out.write("\\hline\n")
            out.write("\\end{longtable}\n")
