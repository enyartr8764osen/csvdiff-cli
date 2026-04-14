"""Command-line interface for csvdiff-cli.

Provides the main entry point for diffing CSV files from the terminal,
with support for configurable key columns and multiple output formats.
"""

import sys
import json
import argparse
from pathlib import Path

from csvdiff.core import load_csv, diff_csv, has_changes, summary


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="csvdiff",
        description="Diff two CSV files and report added, removed, and changed rows.",
    )
    parser.add_argument("original", help="Path to the original CSV file.")
    parser.add_argument("updated", help="Path to the updated CSV file.")
    parser.add_argument(
        "-k",
        "--key",
        dest="keys",
        metavar="COLUMN",
        action="append",
        default=None,
        help=(
            "Column name(s) to use as the row key. "
            "Can be specified multiple times for composite keys. "
            "Defaults to the first column."
        ),
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format: 'text' (default), 'json', or 'summary'.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output in text mode.",
    )
    return parser


def _color(text: str, code: str, use_color: bool) -> str:
    """Wrap text in an ANSI color code if color is enabled."""
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def render_text(result, use_color: bool) -> str:
    """Render a DiffResult as human-readable colored text."""
    lines = []

    for key, row in result.added.items():
        line = f"+ [{', '.join(str(k) for k in key)}] {dict(row)}"
        lines.append(_color(line, "32", use_color))  # green

    for key, row in result.removed.items():
        line = f"- [{', '.join(str(k) for k in key)}] {dict(row)}"
        lines.append(_color(line, "31", use_color))  # red

    for key, (old_row, new_row) in result.changed.items():
        key_str = ', '.join(str(k) for k in key)
        lines.append(_color(f"~ [{key_str}]", "33", use_color))  # yellow
        for field, (old_val, new_val) in sorted(new_row.items()):
            if old_val != new_val:
                lines.append(
                    f"    {field}: "
                    + _color(str(old_val), "31", use_color)
                    + " -> "
                    + _color(str(new_val), "32", use_color)
                )

    return "\n".join(lines)


def render_json(result) -> str:
    """Render a DiffResult as a JSON string."""
    def key_to_str(key):
        return "|".join(str(k) for k in key)

    payload = {
        "added": {key_to_str(k): dict(v) for k, v in result.added.items()},
        "removed": {key_to_str(k): dict(v) for k, v in result.removed.items()},
        "changed": {
            key_to_str(k): {"old": dict(old), "new": dict(new)}
            for k, (old, new) in result.changed.items()
        },
    }
    return json.dumps(payload, indent=2, default=str)


def main(argv=None):
    """Entry point for the csvdiff CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    original_path = Path(args.original)
    updated_path = Path(args.updated)

    for path in (original_path, updated_path):
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(2)

    original_rows = load_csv(original_path)
    updated_rows = load_csv(updated_path)

    # Default key to the first column if not specified
    key_columns = args.keys
    if key_columns is None and original_rows:
        key_columns = [next(iter(original_rows[0].keys()))]

    result = diff_csv(original_rows, updated_rows, key_columns or [])

    if args.output_format == "json":
        print(render_json(result))
    elif args.output_format == "summary":
        s = summary(result)
        print(
            f"Added: {s['added']}  Removed: {s['removed']}  "
            f"Changed: {s['changed']}  Unchanged: {s['unchanged']}"
        )
    else:
        output = render_text(result, use_color=not args.no_color)
        if output:
            print(output)

    sys.exit(1 if has_changes(result) else 0)


if __name__ == "__main__":
    main()
