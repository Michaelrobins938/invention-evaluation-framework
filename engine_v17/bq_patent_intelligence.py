"""Doctorate-level patent intelligence on BigQuery Google Patents public data.

Built on ``engine_v17.bigquery_patents`` (client, normalization, record schema),
this module implements the three institutional research strategies:

A. Deep Novelty / Whitespace mapping  — CPC inventive-code taxonomy combined
   with regex over translated English abstracts.
B. Citation network traversal        — backward + forward citations, classified
   by category (X=novelty-destroying, Y=inventive-step, A=background), with
   bounded-depth graph expansion.
C. "Moat" / assignee landscape       — simple-family concentration by harmonised
   assignee within a CPC space.

COST GUARDRAILS (hard, enforced in every query):
- No ``SELECT *``. Every query projects an explicit, minimal column list.
- ``description_localized`` / ``claims_localized`` are NEVER referenced by the
  broad sweeps (Strategies A/C). They are only touched by
  ``get_patent_full_text``, which requires an exact ``publication_number``.
- Every query runs with ``maximum_bytes_billed`` capped (defaults below), so a
  runaway scan is billed at most the configured ceiling and then errors.
- ``LIMIT`` is applied to every exploratory query.
- Results are returned as bounded ``list[dict]`` (not DataFrames) so the caller
  can chunk for an LLM context window before inserting anything.

Query parameters are bound with ``ScalarQueryParameter``/``ArrayQueryParameter``
(never string-interpolated) for the search functions, so inputs cannot inject
SQL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .bigquery_patents import (
    DATASET,
    BigQueryUnavailable,
    client_factory,
    normalize_publication_number,
    _int_date_to_iso,
)

# ---------------------------------------------------------------------------
# Cost guardrails (bytes billed ceilings). Tuned so an accidental full-table
# scan fails fast instead of billing through the roof.
# ---------------------------------------------------------------------------
MAX_BYTES_BROAD = 1_000_000_000      # 1 GiB  — broad sweeps (A, C)
MAX_BYTES_TARGETED = 100_000_000     # 100 MiB — exact-publication lookups
# (title/abstract/cpc; these prune on the clustered publication_number column).
MAX_BYTES_CITATIONS = 20_000_000_000  # 20 GiB — citation-column queries.
# The citation array column is inherently large: any backward/forward citation
# query scans ~17 GiB even when clustered-pruned on the focal row (≈ $0.11 per
# query at $6.25/TiB). This ceiling still blocks runaway sweeps (full-table
# scans run into the hundreds of GiB) while allowing intentional citation
# traversal. Operators should be aware of the per-query cost before running
# depth>1 trees (fan-out is bounded to 25 per hop).

# Citation categories as they ACTUALLY appear in the public dataset (verified
# live against US-6506148-B2): SEA = examiner search citation, APP = applicant
# citation, PRS = prior-art reference. (EPO X/Y/A search-report codes are NOT
# present for US records; the raw values are passed through verbatim.)
CITATION_CATEGORY_LABELS = {
    "SEA": "examiner search citation",
    "APP": "applicant citation",
    "PRS": "prior-art reference",
    "X": "novelty-destroying (X)",
    "Y": "inventive-step (Y)",
    "A": "background (A)",
}


@dataclass
class CitationNode:
    publication_number: str
    category: str | None
    citation_type: str | None
    role: str  # "backward" (focal cites this) or "forward" (this cites focal)
    depth: int


@dataclass
class CitationTree:
    focal: str
    nodes: list[CitationNode] = field(default_factory=list)

    def backward(self) -> list[CitationNode]:
        return [n for n in self.nodes if n.role == "backward"]

    def forward(self) -> list[CitationNode]:
        return [n for n in self.nodes if n.role == "forward"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "focal": self.focal,
            "nodes": [
                {
                    "publication_number": n.publication_number,
                    "category": n.category,
                    "citation_type": n.citation_type,
                    "role": n.role,
                    "depth": n.depth,
                }
                for n in self.nodes
            ],
        }


def _make_client() -> Any:
    return client_factory()


def _run(client, sql: str, params: list[Any], max_bytes: int) -> list[dict[str, Any]]:
    """Run a parameterised query with a hard bytes-billed ceiling."""
    try:
        from google.cloud import bigquery  # type: ignore

        job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=max_bytes,
            query_parameters=params,
        )
        job = client.query(sql, job_config=job_config)
        return [dict(row.items()) for row in job.result()]
    except Exception as exc:  # pragma: no cover - env dependent
        raise BigQueryUnavailable(f"BigQuery query failed: {exc}") from exc


def _p(name: str, value: str) -> Any:
    from google.cloud import bigquery  # type: ignore

    return bigquery.ScalarQueryParameter(name, "STRING", value)


def _pi(name: str, value: int) -> Any:
    from google.cloud import bigquery  # type: ignore

    return bigquery.ScalarQueryParameter(name, "INT64", value)


# ---------------------------------------------------------------------------
# Strategy A — Deep Novelty / Whitespace mapping
# ---------------------------------------------------------------------------

_STRATEGY_A_SQL = f"""
SELECT
  pub.publication_number AS publication_number,
  pub.family_id AS family_id,
  pub.priority_date AS priority_date,
  pub.grant_date AS grant_date,
  title.text AS title,
  abstract.text AS abstract_text,
  ARRAY(SELECT DISTINCT c.code FROM UNNEST(pub.cpc) AS c WHERE c.code IS NOT NULL) AS cpc_codes
FROM `{DATASET}` AS pub
LEFT JOIN UNNEST(pub.title_localized) AS title ON title.language = 'en'
LEFT JOIN UNNEST(pub.abstract_localized) AS abstract ON abstract.language = 'en'
WHERE
  EXISTS (SELECT 1 FROM UNNEST(pub.cpc) AS cpc_struct
          WHERE cpc_struct.code LIKE @cpc_prefix AND cpc_struct.inventive = TRUE)
  AND REGEXP_CONTAINS(LOWER(COALESCE(abstract.text, '')), @regex_keywords)
  AND pub.grant_date > 0
ORDER BY pub.priority_date DESC
LIMIT @limit
"""


def deep_novelty_search(
    cpc_prefix: str,
    regex_keywords: str,
    limit: int = 100,
    max_bytes: int | None = None,
    *,
    _client=None,
) -> list[dict[str, Any]]:
    """Strategy A — find highly specific prior art / whitespace.

    Args:
        cpc_prefix: CPC inventive sub-group, e.g. ``"A61N2/00%"`` or ``"G06N3/00%"``.
        regex_keywords: BigQuery RE2 regex over the lowercased English abstract,
            e.g. ``r"\\b(transformer|latent space)\\b"``.
        limit: max rows.
        max_bytes: opt-in byte-billing override. A regex over the abstract column
            is a full-table scan (~245 GiB ≈ $1.50); the default ceiling
            (``MAX_BYTES_BROAD``) will reject it. Pass ``max_bytes=250_000_000_000``
            only when the operator has authorised that cost.

    Returns records with ``publication_number``, ``family_id``, ``priority_date``,
    ``grant_date``, ``title``, ``abstract``, ``cpc``.
    """
    from .bigquery_patents import _rows_to_records, _struct_codes, _int_date_to_iso

    client = _make_client() if _client is None else _client
    prefix = cpc_prefix if cpc_prefix.endswith("%") else cpc_prefix + "%"
    rows = _run(
        client,
        _STRATEGY_A_SQL,
        [_p("cpc_prefix", prefix), _p("regex_keywords", regex_keywords), _pi("limit", max(1, int(limit)))],
        max_bytes if max_bytes is not None else MAX_BYTES_BROAD,
    )
    records = _rows_to_records(rows)
    for r, row in zip(records, rows):
        if row.get("priority_date"):
            r["priority_date"] = _int_date_to_iso(row["priority_date"])
        if row.get("abstract_text"):
            r["abstract"] = row["abstract_text"]
    return records


# ---------------------------------------------------------------------------
# Strategy B — Forward & Backward citation network (102/103 risk)
# ---------------------------------------------------------------------------

_BACKWARD_SQL_EQ = f"""
SELECT
  cit.publication_number AS cited_patent,
  cit.category AS category,
  cit.type AS citation_type
FROM `{DATASET}` AS pub
CROSS JOIN UNNEST(pub.citation) AS cit
WHERE pub.publication_number = @target
LIMIT @limit
"""

# Kind-less targets ("US-6506148-%") cannot use the clustered `=` prune; LIKE is
# the fallback (costlier — the MAX_BYTES_TARGETED ceiling still applies).
_BACKWARD_SQL_LIKE = f"""
SELECT
  cit.publication_number AS cited_patent,
  cit.category AS category,
  cit.type AS citation_type
FROM `{DATASET}` AS pub
CROSS JOIN UNNEST(pub.citation) AS cit
WHERE pub.publication_number LIKE @target
LIMIT @limit
"""

_FORWARD_SQL = f"""
SELECT
  pub.publication_number AS citing_patent,
  cit.category AS category,
  cit.type AS citation_type
FROM `{DATASET}` AS pub
CROSS JOIN UNNEST(pub.citation) AS cit
WHERE cit.publication_number LIKE @target
LIMIT @limit
"""


def get_citation_tree(pub_number: str, depth: int = 2, limit: int = 200, *, _client=None) -> CitationTree:
    """Strategy B — traverse the citation graph around a focal patent.

    depth=1: direct backward (what the focal cites) + direct forward (who cites
    the focal). depth>1: expand transitively (BFS) with bounded fan-out.

    Args:
        pub_number: any accepted form ("US6506148B2", "US-6506148-B2", ...).
        depth: traversal depth (default 2).
        limit: max edges retrieved per hop.
    """
    from .bigquery_patents import normalize_publication_number

    client = _make_client() if _client is None else _client
    target = normalize_publication_number(pub_number)
    tree = CitationTree(focal=target)
    backward_sql = _BACKWARD_SQL_EQ if "%" not in target else _BACKWARD_SQL_LIKE

    frontier = [target]
    for d in range(1, int(depth) + 1):
        nxt: list[str] = []
        for pub in frontier:
            back_rows = _run(client, backward_sql, [_p("target", pub), _pi("limit", max(1, int(limit)))], MAX_BYTES_CITATIONS)
            for row in back_rows:
                cited = (row.get("cited_patent") or "").strip()
                if not cited:
                    continue
                tree.nodes.append(CitationNode(
                    publication_number=cited,
                    category=row.get("category"),
                    citation_type=row.get("citation_type"),
                    role="backward",
                    depth=d,
                ))
                if d < int(depth):
                    nxt.append(cited)
            fwd_rows = _run(client, _FORWARD_SQL, [_p("target", pub), _pi("limit", max(1, int(limit)))], MAX_BYTES_CITATIONS)
            for row in fwd_rows:
                citing = (row.get("citing_patent") or "").strip()
                if not citing:
                    continue
                tree.nodes.append(CitationNode(
                    publication_number=citing,
                    category=row.get("category"),
                    citation_type=row.get("citation_type"),
                    role="forward",
                    depth=d,
                ))
                if d < int(depth):
                    nxt.append(citing)
        frontier = list(dict.fromkeys(nxt))[:25]  # bounded fan-out per hop
    return tree


# ---------------------------------------------------------------------------
# Strategy C — the "Moat": assignee landscape
# ---------------------------------------------------------------------------

_STRATEGY_C_SQL = f"""
SELECT
  assignee.name AS assignee_name,
  COUNT(DISTINCT pub.family_id) AS total_patent_families,
  MIN(pub.priority_date) AS earliest_priority
FROM `{DATASET}` AS pub
CROSS JOIN UNNEST(pub.assignee_harmonized) AS assignee
CROSS JOIN UNNEST(pub.cpc) AS cpc_struct
WHERE cpc_struct.code LIKE @cpc_prefix
  AND assignee.name IS NOT NULL
GROUP BY assignee.name
ORDER BY total_patent_families DESC
LIMIT @limit
"""


def assignee_landscape(cpc_prefix: str, limit: int = 20, max_bytes: int | None = None, *, _client=None) -> list[dict[str, Any]]:
    """Strategy C — institutional strength ("moat") by assignee in a CPC space.

    A GROUP BY over the harmonised-assignee + CPC arrays is a large scan (on the
    order of 100+ GiB). ``max_bytes`` is the same explicit opt-in as Strategy A.

    Returns ``[{assignee, total_patent_families, earliest_priority}, ...]``
    ordered by family concentration (continuations/divisionals collapse into one
    ``family_id``).
    """
    from .bigquery_patents import _int_date_to_iso

    client = _make_client() if _client is None else _client
    prefix = cpc_prefix if cpc_prefix.endswith("%") else cpc_prefix + "%"
    rows = _run(
        client,
        _STRATEGY_C_SQL,
        [_p("cpc_prefix", prefix), _pi("limit", max(1, int(limit)))],
        max_bytes if max_bytes is not None else MAX_BYTES_BROAD,
    )
    out = []
    for row in rows:
        name = (row.get("assignee_name") or "").strip()
        if not name:
            continue
        out.append({
            "assignee": name,
            "total_patent_families": int(row.get("total_patent_families") or 0),
            "earliest_priority": _int_date_to_iso(row.get("earliest_priority")),
        })
    return out


# ---------------------------------------------------------------------------
# Targeted full-text (the ONLY function allowed to touch claims/description)
# ---------------------------------------------------------------------------

_FULLTEXT_SQL = f"""
SELECT
  pub.publication_number AS publication_number,
  pub.family_id AS family_id,
  title.text AS title,
  abstract.text AS abstract_text,
  claims.text AS claims_text,
  description.text AS description_text
FROM `{DATASET}` AS pub
LEFT JOIN UNNEST(pub.title_localized) AS title ON title.language = 'en'
LEFT JOIN UNNEST(pub.abstract_localized) AS abstract ON abstract.language = 'en'
LEFT JOIN UNNEST(pub.claims_localized) AS claims ON claims.language = 'en'
LEFT JOIN UNNEST(pub.description_localized) AS description ON description.language = 'en'
WHERE pub.publication_number LIKE @target
LIMIT 1
"""


def get_patent_full_text(pub_number: str, *, _client=None) -> dict[str, Any]:
    """Return title/abstract/claims/description for ONE exact publication.

    This is the only function that reads the massive ``claims_localized`` and
    ``description_localized`` columns, and it requires an exact publication
    number (LIKE against a single normalized number), so the scan stays cheap.
    """
    client = _make_client() if _client is None else _client
    target = normalize_publication_number(pub_number)
    rows = _run(client, _FULLTEXT_SQL, [_p("target", target)], MAX_BYTES_TARGETED)
    if not rows:
        return {}
    row = rows[0]
    out: dict[str, Any] = {}
    for k, v in row.items():
        if v:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# LLM context chunking
# ---------------------------------------------------------------------------

def chunk_records_for_llm(
    records: Iterable[dict[str, Any]],
    max_chars: int = 8_000,
    abstract_budget: int = 600,
) -> list[list[dict[str, Any]]]:
    """Chunk records into LLM-context-friendly batches.

    Each record's abstract is truncated to ``abstract_budget`` chars (a full
    abstract rarely matters for a first pass; the full text is available via
    ``get_patent_full_text``). Batches are cut when the accumulated serialized
    size reaches ``max_chars``.
    """
    import json

    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_size = 0
    for rec in records:
        slim = dict(rec)
        abstract = slim.get("abstract")
        if abstract and len(str(abstract)) > abstract_budget:
            slim["abstract"] = str(abstract)[:abstract_budget] + "..."
            slim["abstract_truncated"] = True
        size = len(json.dumps(slim, default=str))
        if current and current_size + size > max_chars:
            chunks.append(current)
            current = []
            current_size = 0
        current.append(slim)
        current_size += size
    if current:
        chunks.append(current)
    return chunks
