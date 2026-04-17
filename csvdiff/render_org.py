"""Render diff as an Emacs Org-mode table."""
from io import StringIO
from .core import DiffResult


def _column_widths(columns, rows):
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(row.get(c, "")))
    return widths


def _pad(value, width):
    return value.ljust(width)


def _render_table(buf, title, columns, rows):
    if not columns:
        return
    buf.write(f"* {title}\n")
    if not rows:
        buf.write("  /No rows./\n\n")
        return
    widths = _column_widths(columns, rows)
    header = "| " + " | ".join(_pad(c, widths[c]) for c in columns) + " |\n"
    sep = "|" + "+".join("-" * (widths[c] + 2) for c in columns) + "|\n"
    buf.write(header)
    buf.write(sep)
    for row in rows:
        line = "| " + " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns) + " |\n"
        buf.write(line)
    buf.write("\n")


def render_org(diff: DiffResult) -> str:
    buf = StringIO()
    columns = diff.columns
    _render_table(buf, "Added", columns, diff.added)
    _render_table(buf, "Removed", columns, diff.removed)
    changed_old = [c["old"] for c in diff.changed]
    changed_new = [c["new"] for c in diff.changed]
    if columns and diff.changed:
        buf.write("* Changed\n")
        if not diff.changed:
            buf.write("  /No rows./\n\n")
        else:
            widths = _column_widths(columns, changed_old + changed_new)
            header = "| " + " | ".join(_pad(c, widths[c]) for c in columns) + " |\n"
            sep = "|" + "+".join("-" * (widths[c] + 2) for c in columns) + "|\n"
            buf.write("** Before\n")
            buf.write(header)
            buf.write(sep)
            for row in changed_old:
                line = "| " + " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns) + " |\n"
                buf.write(line)
            buf.write("** After\n")
            buf.write(header)
            buf.write(sep)
            for row in changed_new:
                line = "| " + " | ".join(_pad(row.get(c, ""), widths[c]) for c in columns) + " |\n"
                buf.write(line)
            buf.write("\n")
    return buf.getvalue()
