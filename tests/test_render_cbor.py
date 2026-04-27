"""Tests for the CBOR renderer."""

import pytest

cbor2 = pytest.importorskip("cbor2")

from csvdiff.core import DiffResult
from csvdiff.render_cbor import render_cbor


def _empty_diff():
    return DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[],
    )


def _render(diff, **kwargs):
    """Render a DiffResult to CBOR and decode it back to a Python object."""
    data = render_cbor(diff, **kwargs)
    return cbor2.loads(data)


def test_no_changes_produces_empty_sections():
    diff = _empty_diff()
    obj = _render(diff)
    assert obj["added"] == []
    assert obj["removed"] == []
    assert obj["changed"] == []


def test_empty_diff_has_three_sections():
    diff = _empty_diff()
    obj = _render(diff)
    assert set(obj.keys()) >= {"added", "removed", "changed"}


def test_added_row_appears_in_added_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[],
    )
    obj = _render(diff)
    assert len(obj["added"]) == 1
    assert obj["added"][0]["row"]["id"] == "1"
    assert obj["added"][0]["row"]["name"] == "Alice"


def test_removed_row_appears_in_removed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[],
    )
    obj = _render(diff)
    assert len(obj["removed"]) == 1
    assert obj["removed"][0]["row"]["id"] == "2"
    assert obj["removed"][0]["row"]["name"] == "Bob"


def test_changed_row_appears_in_changed_section():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[],
        changed=[
            (
                {"id": "3", "name": "Carol"},
                {"id": "3", "name": "Caroline"},
            )
        ],
    )
    obj = _render(diff)
    assert len(obj["changed"]) == 1
    entry = obj["changed"][0]
    assert entry["old"]["name"] == "Carol"
    assert entry["new"]["name"] == "Caroline"


def test_key_included_in_added_record():
    diff = DiffResult(
        columns=["id", "name"],
        added=[{"id": "10", "name": "Dave"}],
        removed=[],
        changed=[],
    )
    obj = _render(diff, keys=["id"])
    record = obj["added"][0]
    assert "key" in record
    assert record["key"] == {"id": "10"}


def test_key_included_in_removed_record():
    diff = DiffResult(
        columns=["id", "name"],
        added=[],
        removed=[{"id": "11", "name": "Eve"}],
        changed=[],
    )
    obj = _render(diff, keys=["id"])
    record = obj["removed"][0]
    assert "key" in record
    assert record["key"] == {"id": "11"}


def test_output_is_bytes():
    diff = _empty_diff()
    result = render_cbor(diff)
    assert isinstance(result, bytes)


def test_multiple_added_rows_all_present():
    diff = DiffResult(
        columns=["id", "name"],
        added=[
            {"id": "1", "name": "Alice"},
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Carol"},
        ],
        removed=[],
        changed=[],
    )
    obj = _render(diff)
    assert len(obj["added"]) == 3
    names = [r["row"]["name"] for r in obj["added"]]
    assert "Alice" in names
    assert "Bob" in names
    assert "Carol" in names
