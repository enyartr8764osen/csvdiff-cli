"""Render diff as BBCode (bulletin board code) tables."""
from io import StringIO
from .core import DiffResult, has_changes


def _column_widths(rows: list[dict], columns: list[str]) -> dict[str, int]:
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))
    return widths


def _pad(value: str, width: int) -> str:
    return str(value).ljust(width)


def _render_table(title: str, rows: list[dict], columns: list[str], buf: StringIO) -> None:
    if not rows:
        return
    widths = _column_widths(rows, columns)
    buf.write(f"[b]{title}[/b]\n")
    buf.write("[table]\n")
    header_cells = "".join(f"[th]{_pad(c, widths[c])}[/th]" for c in columns)
    buf.write(f"[tr]{header_cells}[/tr]\n")
    for row in rows:
        cells = "".join(f"[td]{_pad(row.get(c, ''), widths[c])}[/td]" for c in columns)
        buf.write(f"[tr]{cells}[/tr]\n")
    buf.write("[/table]\n")


def render_bbcode(diff: DiffResult) -> str:
    if not has_changes(diff):
        return ""
    columns = diff.columns
    if not columns:
        return ""
    buf = StringIO()
    _render_table("Added Rows", diff.added, columns, buf)
    if diff.added and (diff.removed or diff.changed):
        buf.write("\n")
    _render_table("Removed Rows", diff.removed, columns, buf)
    if diff.removed and diff.changed:
        buf.write("\n")
    if diff.changed:
        buf.write("[b]Changed Rows[/b]\n")
        for old, new in diff.changed:
            buf.write("[table]\n")
            header_cells = "".join(f"[th]{c}[/th]" for c in columns)
            buf.write(f"[tr]{header_cells}[/tr]\n")
            old_cells = "".join(f"[td][color=red]{old.get(c, '')}[/color][/td]" for c in columns)
            buf.write(f"[tr]{old_cells}[/tr]\n")
            new_cells = "".join(f"[td][color=green]{new.get(c, '')}[/color][/td]" for c in columns)
            buf.write(f"[tr]{new_cells}[/tr]\n")
            buf.write("[/table]\n")
    return buf.getvalue().rstrip("\n")
