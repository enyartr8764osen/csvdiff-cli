"""Additional quoting edge-case tests for csvdiff.render_yaml._quote."""
from __future__ import annotations

import pytest

from csvdiff.render_yaml import _quote


@pytest.mark.parametrize(
    "value, expected",
    [
        ("plain", "plain"),
        ("with space", "with space"),
        ("", '""'),
        ("foo: bar", '"foo: bar"'),
        ("#comment", '"#comment"'),
        ("{dict}", '"{dict}"'),
        ("[list]", '"[list]"'),
        ("  leading", '"  leading"'),
        ("trailing  ", '"trailing  "'),
        ('say "hi"', 'say \\"hi\\"'.join(['"', '"'])),
        ("100", "100"),
        ("key: value", '"key: value"'),
        ("pipe|char", '"pipe|char"'),
        ("amp&ersand", '"amp&ersand"'),
    ],
)
def test_quote(value: str, expected: str):
    # For the embedded-quote case we build expected inline to avoid confusion
    if value == 'say "hi"':
        assert _quote(value) == '"say \\"hi\\""'
    else:
        assert _quote(value) == expected
