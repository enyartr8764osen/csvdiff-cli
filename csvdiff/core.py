"""Core CSV diffing logic for csvdiff-cli."""

import csv
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class DiffResult:
    """Holds the result of a CSV diff operation."""

    added: List[Dict] = field(default_factory=list)
    removed: List[Dict] = field(default_factory=list)
    modified: List[Tuple[Dict, Dict]] = field(default_factory=list)
    key_columns: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    @property
    def summary(self) -> str:
        return (
            f"Added: {len(self.added)}, "
            f"Removed: {len(self.removed)}, "
            f"Modified: {len(self.modified)}"
        )


def _make_key(row: Dict, key_columns: List[str]) -> Tuple:
    """Extract a hashable key from a row using the specified key columns."""
    return tuple(row.get(col, "") for col in key_columns)


def load_csv(filepath: str) -> Tuple[List[str], List[Dict]]:
    """Load a CSV file and return (headers, rows)."""
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return list(headers), rows


def diff_csvs(
    old_path: str,
    new_path: str,
    key_columns: Optional[List[str]] = None,
) -> DiffResult:
    """Diff two CSV files and return a DiffResult."""
    old_headers, old_rows = load_csv(old_path)
    new_headers, new_rows = load_csv(new_path)

    if key_columns is None:
        key_columns = old_headers[:1]

    missing = [c for c in key_columns if c not in old_headers]
    if missing:
        raise ValueError(f"Key columns not found in old CSV: {missing}")

    old_index: Dict[Tuple, Dict] = {_make_key(r, key_columns): r for r in old_rows}
    new_index: Dict[Tuple, Dict] = {_make_key(r, key_columns): r for r in new_rows}

    old_keys: Set[Tuple] = set(old_index.keys())
    new_keys: Set[Tuple] = set(new_index.keys())

    result = DiffResult(key_columns=key_columns)
    result.removed = [old_index[k] for k in old_keys - new_keys]
    result.added = [new_index[k] for k in new_keys - old_keys]

    for key in old_keys & new_keys:
        old_row = old_index[key]
        new_row = new_index[key]
        if old_row != new_row:
            result.modified.append((old_row, new_row))

    return result
