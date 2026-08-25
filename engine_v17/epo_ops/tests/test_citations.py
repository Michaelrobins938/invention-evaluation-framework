"""Tests for patent-number normalization to OPS dotted format."""

from __future__ import annotations

import pytest

from engine_v17.epo_ops.citations import (
    _normalize_patent_number,
    normalize_patent_number,
)


class TestNormalizePatentNumber:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("US5215088", "US.5215088"),
            ("US5215088A", "US.5215088.A"),
            ("US8527057B2", "US.8527057.B2"),
            ("EP1664047", "EP.1664047"),
            ("EP1664047A1", "EP.1664047.A1"),
            ("us5215088a", "US.5215088.A"),
            # already-dotted forms pass through unchanged (idempotent)
            ("US.5215088.A", "US.5215088.A"),
            ("EP.1664047.A1", "EP.1664047.A1"),
        ],
    )
    def test_dotted_forms(self, raw, expected):
        assert normalize_patent_number(raw) == expected

    def test_private_alias_matches_public(self):
        assert _normalize_patent_number("US5215088A") == normalize_patent_number("US5215088A")
