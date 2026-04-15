"""HTML rendering for CSV diff results."""

from .core import DiffResult, has_changes


def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _row_to_cells(row: dict, headers: list[str], tag: str = "td") -> str:
    cells = "".join(
        f"<{tag}>{_escape(str(row.get(h, '')))}</{tag}>"
        for h in headers
    )
    return cells


def _render_table(title: str, rows: list[dict], headers: list[str], css_class: str) -> str:
    if not rows:
        return ""
    header_cells = "".join(f"<th>{_escape(h)}</th>" for h in headers)
    body_rows = "".join(
        f"<tr>{_row_to_cells(row, headers)}</tr>" for row in rows
    )
    return (
        f"<section class='{css_class}'>\n"
        f"  <h2>{_escape(title)}</h2>\n"
        f"  <table>\n"
        f"    <thead><tr>{header_cells}</tr></thead>\n"
        f"    <tbody>{body_rows}</tbody>\n"
        f"  </table>\n"
        f"</section>\n"
    )


def render_html(diff: DiffResult) -> str:
    """Render a DiffResult as a self-contained HTML document."""
    if not has_changes(diff):
        return (
            "<!DOCTYPE html><html><body>"
            "<p class='no-changes'>No differences found.</p>"
            "</body></html>"
        )

    headers = diff.headers

    added_section = _render_table("Added Rows", diff.added, headers, "added")
    removed_section = _render_table("Removed Rows", diff.removed, headers, "removed")

    changed_rows_old = [change["old"] for change in diff.changed]
    changed_rows_new = [change["new"] for change in diff.changed]
    changed_section = ""
    if diff.changed:
        changed_section = (
            _render_table("Changed Rows (Before)", changed_rows_old, headers, "changed-old")
            + _render_table("Changed Rows (After)", changed_rows_new, headers, "changed-new")
        )

    style = (
        "<style>"
        ".added table { border-collapse: collapse; } "
        ".added td, .added th { border: 1px solid #ccc; padding: 4px 8px; } "
        ".added { background: #eaffea; } "
        ".removed { background: #ffeaea; } "
        ".changed-old { background: #fff3cd; } "
        ".changed-new { background: #d1ecf1; } "
        "table { border-collapse: collapse; margin-bottom: 1em; } "
        "td, th { border: 1px solid #ccc; padding: 4px 8px; }"
        "</style>"
    )

    body = added_section + removed_section + changed_section
    return f"<!DOCTYPE html><html><head>{style}</head><body>\n{body}</body></html>"
