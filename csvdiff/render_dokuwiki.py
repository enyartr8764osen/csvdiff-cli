"""Render a DiffResult as DokuWiki table markup."""
from io import StringIO
from csvdiff.core import DiffResult


def _column_widths(rows: list[dict], columns: list[str]) -> dict[str, int]:
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))
    return widths


def _pad(value: str, width: int) -> str:
    return str(value).ljust(width)


def _render_table(rows: list[dict], columns: list[str], out: StringIO) -> None:
    if not rows:
        return
    widths = _column_widths(rows, columns)
    header = "^ " + " ^ ".join(_pad(c, widths[c]) for c in columns) + " ^"
    out.write(header + "\n")
    for row in rows:
        line = "| " + " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns) + " |"
        out.write(line + "\n")


def render_dokuwiki(diff: DiffResult) -> str:
    if not diff.columns:
        return ""
    out = StringIO()
    sections = [
        ("===== Added Rows =====", diff.added),
        ("===== Removed Rows =====", diff.removed),
    ]
    changed_old = [old for old, _ in diff.changed]
    changed_new = [new for _, new in diff.changed]

    written = False
    for title, rows in sections:
        if rows:
            if written:
                out.write("\n")
            out.write(title + "\n")
            _render_table(rows, diff.columns, out)
            written = True

    if diff.changed:
        if written:
            out.write("\n")
        out.write("===== Changed Rows (Before) =====\n")
        _render_table(changed_old, diff.columns, out)
        out.write("\n===== Changed Rows (After) =====\n")
        _render_table(changed_new, diff.columns, out)

    return out.getvalue()
