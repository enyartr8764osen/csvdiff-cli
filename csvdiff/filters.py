"""Column and row filtering utilities for csvdiff."""

from typing import List, Optional, Dict, Any


def filter_columns(
    rows: List[Dict[str, Any]],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Return rows with only the specified columns included or excluded.

    Args:
        rows: List of row dicts.
        include: If provided, only these columns are kept.
        exclude: If provided, these columns are removed.

    Returns:
        Filtered list of row dicts.

    Raises:
        ValueError: If both include and exclude are specified.
    """
    if include and exclude:
        raise ValueError("Specify either 'include' or 'exclude', not both.")

    if not rows:
        return rows

    if include:
        missing = set(include) - set(rows[0].keys())
        if missing:
            raise ValueError(f"Columns not found in data: {sorted(missing)}")
        return [{col: row[col] for col in include if col in row} for row in rows]

    if exclude:
        return [{k: v for k, v in row.items() if k not in exclude} for row in rows]

    return rows


def filter_rows_by_column(
    rows: List[Dict[str, Any]],
    column: str,
    value: str,
) -> List[Dict[str, Any]]:
    """Return only rows where column equals value.

    Args:
        rows: List of row dicts.
        column: Column name to filter on.
        value: Value to match (string comparison).

    Returns:
        Filtered list of row dicts.

    Raises:
        ValueError: If column does not exist in the data.
    """
    if rows and column not in rows[0]:
        raise ValueError(f"Column '{column}' not found in data.")
    return [row for row in rows if row.get(column) == value]


def normalize_whitespace(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Strip leading/trailing whitespace from all string values."""
    return [
        {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
        for row in rows
    ]
