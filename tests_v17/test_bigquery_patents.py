"""Tests for the BigQuery Google Patents adapter (engine_v17.bigquery_patents).

Hermetic: these tests do NOT require BigQuery credentials, a GCP project, or a
network call. They validate the SQL generation, the record→schema mapping, the
graceful-degradation failure path, and that the module is import-safe when
BigQuery is absent. Live-query behaviour is exercised separately via
scripts/test_bigquery_search.py --run.
"""

from __future__ import annotations

import threading

import pytest

from engine_v17 import bigquery_patents as bq


# ---------------------------------------------------------------------------
# SQL generation (no client required — builders are pure)
# ---------------------------------------------------------------------------


def test_keyword_sql_single_term():
    sql = bq._keyword_sql(["resonance"])
    assert "LOWER(title.text)" in sql
    assert "LOWER(abstract.text)" in sql
    assert "%resonance%" in sql
    assert sql.count("OR") == 1  # title OR abstract, single term -> no AND


def test_keyword_sql_conjunction_and_escaping():
    sql = bq._keyword_sql(["50%_phi", "field"])
    # every term present
    assert "%50\\%\\_phi%" in sql
    assert "%field%" in sql
    assert "AND" in sql


def test_keyword_sql_requires_term():
    with pytest.raises(ValueError):
        bq._keyword_sql([])
    with pytest.raises(ValueError):
        bq._keyword_sql(["   "])


def test_apply_limit_appends_and_replaces():
    sql = bq._apply_limit("SELECT 1", 25)
    assert sql.endswith("LIMIT 25")
    # existing trailing limit is replaced, not doubled
    replaced = bq._apply_limit("SELECT 1\nLIMIT 999", 10)
    assert replaced.endswith("LIMIT 10")
    assert "999" not in replaced


def test_rows_to_records_schema_contract():
    """Records must expose the keys landscape.normalize_landscape and the
    metadata/claims readers consume."""
    rows = [
        {
            "publication_number": "US-6506148-B2",
            "grant_date": 20030114,
            "title": "Nervous system manipulation",
            "cpc_codes": [{"code": "A61N2/00"}, {"code": "A61M21/00"}],
            "ipc_codes": [{"code": "A61N2/00"}],
        }
    ]
    records = bq._rows_to_records(rows)
    assert len(records) == 1
    rec = records[0]
    # landscape normaliser keys
    assert rec["publication_number"] == "US-6506148-B2"
    assert rec["family_id"] == "US-6506148-B2"
    assert "relevance" in rec
    assert rec["relevance"]["adjacent"] is True
    # metadata keys
    assert rec["title"] == "Nervous system manipulation"
    assert rec["grant_date"] == "2003-01-14"  # INT64 YYYYMMDD -> ISO
    assert rec["cpc"] == ["A61N2/00", "A61M21/00"]


def test_rows_to_records_omits_empty_and_derives_family():
    records = bq._rows_to_records([{"publication_number": "WO123", "title": None}])
    rec = records[0]
    assert rec["publication_number"] == "WO123"
    assert rec["family_id"] == "WO123"
    assert "title" not in rec  # None omitted, never invented
    assert "grant_date" not in rec


# ---------------------------------------------------------------------------
# Virtual client (no live BigQuery) exercising the public search functions
# ---------------------------------------------------------------------------


class _VirtualClient:
    """Minimal stand-in exposing .query() so the public functions' control flow
    (query build + row mapping) can be tested without BigQuery."""

    def __init__(self, rows):
        self._rows = rows

    def query(self, sql, job_config=None):  # noqa: ANN001
        q = _VirtualClient._Job(self._rows)
        return q

    class _Job:
        def __init__(self, rows):
            self._rows = rows

        def result(self):
            return self._rows


def _rows(dicts):
    return [_Row(d) for d in dicts]


class _Row:
    """Minimal row stand-in exposing .items() (BigQuery row api)."""

    def __init__(self, data):
        self._data = data

    def items(self):
        return self._data.items()


def test_search_by_keywords_invokes_query_and_maps(tmp_path):
    client = _VirtualClient(
        _rows([{"publication_number": "US6506148B2", "title": "sensory resonance screen"}])
    )
    records = bq.search_patents_by_keywords(["resonance"], limit=5, _client=client)
    assert records
    assert records[0]["publication_number"] == "US6506148B2"


def test_search_by_cpc_with_keywords(tmp_path):
    client = _VirtualClient(_rows([{"publication_number": "EP001", "cpc_codes": ["A61N2/00"]}]))
    records = bq.search_patents_by_cpc("A61N2", keywords=["resonance"], limit=5, _client=client)
    assert records[0]["publication_number"] == "EP001"


def test_get_by_publication_number_found_and_missing(tmp_path):
    found = _VirtualClient(_rows([{"publication_number": "US6506148B2"}]))
    rec = bq.get_patent_by_publication_number("US6506148B2", _client=found)
    assert rec.get("publication_number") == "US6506148B2"

    missing = _VirtualClient(_rows([]))
    rec = bq.get_patent_by_publication_number("US0000000", _client=missing)
    assert rec == {}


# ---------------------------------------------------------------------------
# Graceful degradation / failure path
# ---------------------------------------------------------------------------


def test_cpc_prefix_required():
    with pytest.raises(ValueError):
        bq.search_patents_by_cpc("  ", _client=_VirtualClient(_rows([])))


def test_pub_number_required():
    with pytest.raises(ValueError):
        bq.get_patent_by_publication_number("  ", _client=_VirtualClient(_rows([])))


def test_bigquery_unavailable_import_err(monkeypatch, tmp_path):
    """When google.cloud.bigquery cannot be imported, client_factory must raise
    BigQueryUnavailable (never a bare ImportError)."""

    import builtins
    import sys

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        # `from google.cloud import bigquery` first imports 'google.cloud',
        # then 'google.cloud.bigquery' — block the whole namespace so the
        # failure is deterministic regardless of module-cache state.
        if name.startswith("google.cloud"):
            raise ImportError("simulated missing google-cloud-bigquery")
        return real_import(name, *a, **k)

    for mod in [m for m in list(sys.modules) if m.startswith("google.cloud")]:
        monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(bq.BigQueryUnavailable):
        bq.client_factory()


def test_bigquery_unavailable_is_runtime_error():
    assert issubclass(bq.BigQueryUnavailable, RuntimeError)


# ---------------------------------------------------------------------------
# Publication-number normalization (hyphenated dataset format)
# ---------------------------------------------------------------------------


def test_normalize_publication_number_compact_with_kind():
    assert bq.normalize_publication_number("US6506148B2") == "US-6506148-B2"


def test_normalize_publication_number_without_kind_gives_like_pattern():
    assert bq.normalize_publication_number("US6506148") == "US-6506148-%"


def test_normalize_publication_number_hyphenated_and_case():
    assert bq.normalize_publication_number("us-6506148-b2") == "US-6506148-B2"
    assert bq.normalize_publication_number("ep1234567a1") == "EP-1234567-A1"


def test_normalize_publication_number_invalid():
    with pytest.raises(ValueError):
        bq.normalize_publication_number("12345")
    with pytest.raises(ValueError):
        bq.normalize_publication_number("not a patent")


def test_int_date_to_iso():
    assert bq._int_date_to_iso(20030114) == "2003-01-14"
    assert bq._int_date_to_iso(0) is None
    assert bq._int_date_to_iso(None) is None


def test_struct_codes_flattens():
    assert bq._struct_codes([{"code": "A61N2/00"}, {"code": "A61M21/00"}]) == ["A61N2/00", "A61M21/00"]
    assert bq._struct_codes(["A61B5/04"]) == ["A61B5/04"]
    assert bq._struct_codes(None) == []
    assert bq._struct_codes([{"no_code": 1}]) == []
