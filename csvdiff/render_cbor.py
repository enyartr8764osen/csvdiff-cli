"""Render a DiffResult as CBOR (Concise Binary Object Representation).

CBOR is a binary data format (RFC 7049) that is compact and widely supported.
The output mirrors the JSON renderer's structure but encoded as CBOR bytes.
"""

from __future__ import annotations

from typing import IO

try:
    import cbor2
    _CBOR2_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CBOR2_AVAILABLE = False

from csvdiff.core import DiffResult


def _row_to_obj(row: dict[str, str]) -> dict[str, str]:
    """Return a plain dict suitable for CBOR serialisation."""
    return dict(row)


def _key_to_obj(key: tuple[str, ...], key_cols: list[str]) -> dict[str, str]:
    """Map a key tuple back to a labelled dict using *key_cols*."""
    return dict(zip(key_cols, key))


def render_cbor(
    diff: DiffResult,
    stream: IO[bytes],
    *,
    key_cols: list[str] | None = None,
) -> None:
    """Write *diff* to *stream* as a CBOR-encoded map.

    The top-level CBOR value is a map with three keys:

    * ``"added"``   – list of added row objects
    * ``"removed"`` – list of removed row objects
    * ``"changed"`` – list of change objects, each with ``"key"``,
      ``"before"``, and ``"after"`` fields

    Args:
        diff:     The computed diff result.
        stream:   A binary-mode writable stream.
        key_cols: Column names that form the row key (used to label change
                  entries).  Defaults to an empty list.

    Raises:
        ImportError: If the ``cbor2`` package is not installed.
    """
    if not _CBOR2_AVAILABLE:
        raise ImportError(
            "The 'cbor2' package is required for CBOR output.  "
            "Install it with: pip install cbor2"
        )

    if key_cols is None:
        key_cols = []

    added = [_row_to_obj(row) for row in diff.added]
    removed = [_row_to_obj(row) for row in diff.removed]
    changed = [
        {
            "key": _key_to_obj(key, key_cols),
            "before": _row_to_obj(before),
            "after": _row_to_obj(after),
        }
        for key, (before, after) in diff.changed.items()
    ]

    payload: dict[str, object] = {
        "added": added,
        "removed": removed,
        "changed": changed,
    }

    cbor2.dump(payload, stream)
