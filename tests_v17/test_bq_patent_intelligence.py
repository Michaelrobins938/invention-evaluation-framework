"""Hermetic tests for engine_v17.bq_patent_intelligence (no credentials needed).

Covers: citation-tree dataclass, SQL generation, chunking, cost-guardrail
constants, and the virtual-client control flow of the strategy functions.
Live-query behaviour is validated via scripts/test_bq_intelligence.py (dry-run
is free; live runs bill the project).
"""

from __future__ import annotations

import pytest

from engine_v17 import bq_patent_intelligence as bi


# ---------------------------------------------------------------------------
# CitationTree dataclass
# ---------------------------------------------------------------------------


def test_citation_tree_roles_and_serialisation():
    tree = bi.CitationTree(focal="US-6506148-B2")
    tree.nodes.append(bi.CitationNode("US-1-A", "SEA", None, "backward", 1))
    tree.nodes.append(bi.CitationNode("US-2-A", "APP", None, "forward", 1))
    assert len(tree.backward()) == 1
    assert len(tree.forward()) == 1
    d = tree.to_dict()
    assert d["focal"] == "US-6506148-B2"
    assert d["nodes"][0]["role"] == "backward"
    assert d["nodes"][1]["category"] == "APP"


def test_citation_category_labels_reflect_real_dataset():
    # Verified live against US-6506148-B2: SEA/APP/PRS are the real values.
    assert "SEA" in bi.CITATION_CATEGORY_LABELS
    assert "APP" in bi.CITATION_CATEGORY_LABELS
    assert "PRS" in bi.CITATION_CATEGORY_LABELS


# ---------------------------------------------------------------------------
# SQL generation
# ---------------------------------------------------------------------------


def test_strategy_a_sql_has_cost_guardrail_shape():
    sql = bi._STRATEGY_A_SQL
    assert "SELECT" in sql
    # guardrails: no SELECT *, no description/claims columns
    assert "SELECT *" not in sql
    assert "description_localized" not in sql
    assert "claims_localized" not in sql
    assert "abstract_localized" in sql
    assert "@cpc_prefix" in sql
    assert "@regex_keywords" in sql
    assert "cpc_struct.inventive = TRUE" in sql
    assert "LIMIT @limit" in sql


def test_strategy_b_sql():
    assert "@target" in bi._BACKWARD_SQL_EQ
    assert "@target" in bi._BACKWARD_SQL_LIKE
    assert "@target" in bi._FORWARD_SQL
    assert "cit.category" in bi._BACKWARD_SQL_EQ
    assert "SELECT *" not in bi._BACKWARD_SQL_EQ


def test_strategy_c_sql():
    assert "assignee_harmonized" in bi._STRATEGY_C_SQL
    assert "COUNT(DISTINCT pub.family_id)" in bi._STRATEGY_C_SQL
    assert "GROUP BY assignee.name" in bi._STRATEGY_C_SQL
    assert "SELECT *" not in bi._STRATEGY_C_SQL


def test_fulltext_is_the_only_claims_description_reader():
    # Cost guardrail: the massive columns appear ONLY in the targeted full-text query.
    assert "claims_localized" in bi._FULLTEXT_SQL
    assert "description_localized" in bi._FULLTEXT_SQL
    for sql in (bi._STRATEGY_A_SQL, bi._BACKWARD_SQL_EQ, bi._BACKWARD_SQL_LIKE, bi._FORWARD_SQL, bi._STRATEGY_C_SQL):
        assert "claims_localized" not in sql
        assert "description_localized" not in sql


# ---------------------------------------------------------------------------
# Cost guardrails
# ---------------------------------------------------------------------------


def test_cost_guardrail_defaults_block_runaway_scans():
    # defaults must be far below a full 900GB-table scan
    assert bi.MAX_BYTES_BROAD < 10_000_000_000
    assert bi.MAX_BYTES_TARGETED < bi.MAX_BYTES_CITATIONS
    assert bi.MAX_BYTES_CITATIONS < 100_000_000_000


# ---------------------------------------------------------------------------
# Virtual client control flow
# ---------------------------------------------------------------------------


class _Row:
    def __init__(self, data):
        self._data = data

    def items(self):
        return self._data.items()


class _Job:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class _VirtualClient:
    def __init__(self, rows):
        self._rows = rows

    def query(self, sql, job_config=None):
        return _Job(self._rows)


def _rows(dicts):
    return [_Row(d) for d in dicts]


def test_citation_tree_uses_virtual_client(monkeypatch):
    # Backward rows for the focal; forward query returns one citing patent.
    def fake_run(client, sql, params, max_bytes):
        if "pub.publication_number = @target" in sql or "pub.publication_number LIKE @target" in sql:
            return [{"cited_patent": "US-3592965-A", "category": "SEA", "citation_type": None}]
        return [{"citing_patent": "US-2011082366-A1", "category": "PRS", "citation_type": None}]

    monkeypatch.setattr(bi, "_run", fake_run)
    client = _VirtualClient([])
    tree = bi.get_citation_tree("US6506148B2", depth=1, limit=50, _client=client)
    assert tree.focal == "US-6506148-B2"
    assert [n.publication_number for n in tree.backward()] == ["US-3592965-A"]
    assert [n.publication_number for n in tree.forward()] == ["US-2011082366-A1"]


def test_assignee_landscape_maps_rows(monkeypatch):
    def fake_run(client, sql, params, max_bytes):
        return [
            {"assignee_name": "Ascension Technology", "total_patent_families": 42, "earliest_priority": 19990101},
        ]

    monkeypatch.setattr(bi, "_run", fake_run)
    out = bi.assignee_landscape("A61N2", limit=5, _client=_VirtualClient([]))
    assert out == [{"assignee": "Ascension Technology", "total_patent_families": 42, "earliest_priority": "1999-01-01"}]


# ---------------------------------------------------------------------------
# LLM context chunking
# ---------------------------------------------------------------------------


def test_chunk_records_for_llm_batches_and_truncates():
    recs = [
        {"publication_number": "A", "abstract": "x" * 3000},
        {"publication_number": "B", "abstract": "short"},
        {"publication_number": "C", "abstract": "y" * 3000},
    ]
    # max_chars=300: each truncated record serialises ~210 chars, so A|B|C split
    # into three separate chunks deterministically.
    chunks = bi.chunk_records_for_llm(recs, max_chars=300, abstract_budget=200)
    assert len(chunks) == 3
    assert all(len(c) == 1 for c in chunks)
    # truncated abstract has the flag and the budget cap
    assert chunks[0][0]["abstract_truncated"] is True
    assert len(chunks[0][0]["abstract"]) <= 200 + 3
    assert chunks[1][0]["publication_number"] == "B"
    assert "abstract_truncated" not in chunks[1][0]  # short abstract untouched


def test_chunk_records_for_llm_empty():
    assert bi.chunk_records_for_llm([]) == []


def test_get_patent_full_text_virtual(monkeypatch):
    def fake_run(client, sql, params, max_bytes):
        return [{"publication_number": "US-6506148-B2", "claims_text": "1. A method...", "description_text": "FIELD"}]

    monkeypatch.setattr(bi, "_run", fake_run)
    out = bi.get_patent_full_text("US6506148B2", _client=_VirtualClient([]))
    assert out["publication_number"] == "US-6506148-B2"
    assert "claims_text" in out
    assert "description_text" in out
