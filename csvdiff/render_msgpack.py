"""Render a DiffResult as a MessagePack binary blob.

The output schema mirrors the JSON renderer:

    {
        "added":   [ {col: val, ...}, ... ],
        "removed": [ {col: val, ...}, ... ],
        "changed": [
            {
                "key":    {key_col: val, ...},
                "before": {col: val, ...},
                "after":  {col: val, ...},
            },
            ...
        ],
    }

Requires the ``msgpack`` package (``pip install msgpack``).
"""

from __future__ import annotations

from typing import IO

try:
    import msgpack  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The msgpack renderer requires the 'msgpack' package. "
        "Install it with: pip install msgpack"
    ) from exc

from csvdiff.core import DiffResult


def _row_to_obj(row: dict[str, str]) -> dict[str, str]:
    """Return a plain dict suitable for msgpack serialisation."""
    return dict(row)


def _key_to_obj(key: tuple[str, ...], columns: list[str]) -> dict[str, str]:
    """Convert a key tuple back to a labelled dict using *columns*."""
    return dict(zip(columns, key))


def render_msgpack(
    diff: DiffResult,
    stream: IO[bytes],
    *,
    key_columns: list[str] | None = None,
) -> None:
    """Serialise *diff* as MessagePack and write to *stream*.

    Parameters
    ----------
    diff:
        The diff result produced by :func:`csvdiff.core.diff`.
    stream:
        A writable **binary** stream.
    key_columns:
        Column names that form the row key.  Used to reconstruct the key
        object inside each ``changed`` entry.  When *None* the key tuple
        values are stored as a plain list instead of a labelled dict.
    """
    added = [_row_to_obj(row) for row in diff.added]

    removed = [_row_to_obj(row) for row in diff.removed]

    changed = []
    for key, (before, after) in diff.changed.items():
        if key_columns is not None:
            key_obj: dict[str, str] | list[str] = _key_to_obj(
                key, key_columns
            )
        else:
            key_obj = list(key)
        changed.append(
            {
                "key": key_obj,
                "before": _row_to_obj(before),
                "after": _row_to_obj(after),
            }
        )

    payload = {
        "added": added,
        "removed": removed,
        "changed": changed,
    }

    stream.write(msgpack.packb(payload, use_bin_type=True))
