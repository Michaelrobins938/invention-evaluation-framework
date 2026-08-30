"""BigQuery Google Patents public-dataset adapter.

This module provides a SQL-first alternative to the rate-limited HTTP patent
search endpoints (Google Patents web pages, EPO OPS HTTP). It queries the public
Google Patents BigQuery dataset ``patents-public-data.patents.publications``:

* bulk prior-art retrieval by keyword against the localised title / abstract;
* CPC / IPC classification search;
* exact lookup by publication number.

It is designed to be *schema-compatible* with the downstream evaluation models:

* ``landscape.normalize_landscape`` consumes records with ``publication_number``,
  ``family_id``, ``assignee`` and ``relevance``.
* ``patent_source._rows`` / ``domain_parsers.parse_patent_metadata`` use
  ``publication_number``, ``title``, ``publication_date``, ``backward_references``,
  ``forward_references``.

Records returned here therefore use those keys so they can drop directly into the
existing normalisation/metadata pipeline.

Graceful degradation: every function lazily builds the client. If BigQuery is not
installed, credentials are missing, or a non-retryable error occurs, the module
raises ``BigQueryUnavailable`` (a subclass of ``RuntimeError``) so callers can fall
back to the HTTP live-adapter path instead of crashing the pipeline. No query
executes or bills until a function is actually called.

Dataset / schema notes
----------------------
The public dataset is denormalised; array fields are repeated within a row:

    publication_number   STRING   e.g. "US6506148B2"
    title_localized      ARRAY<STRUCT<text STRING, language STRING>>
    abstract_localized   ARRAY<STRUCT<text STRING, language STRING>>
    cpc                  ARRAY<STRUCT<code STRING, ...>>
    ipc                  ARRAY<STRUCT<code STRING, ...>>
    assignee             ARRAY<STRUCT<...>>
    inventor             ARRAY<STRUCT<...>>
    language             STRING   primary language of the document
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

# Dataset identifiers (Google Patents public dataset).
DATASET = "patents-public-data.patents.publications"

# Preferred text field per record; lower-cased for clean inclusion in query.
_EN = "en"

# A stable, minimal SELECT used by every query. We project publication-level
# identifiers and the localised English title/abstract via UNNEST, plus the
# commonly-needed metadata the downstream models read. We alias the flattened
# values so they can be mapped directly onto the record schema. ``cpc``/``ipc``
# are ARRAY<STRUCT<...>> columns — projected whole and flattened in Python.
_SELECT = f"""SELECT
    pub.publication_number AS publication_number,
    pub.grant_date AS grant_date,
    pub.publication_date AS publication_date,
    title.text AS title,
    abstract.text AS abstract_text,
    pub.cpc AS cpc_codes,
    pub.ipc AS ipc_codes,
    CAST(NULL AS STRING) AS assignee
  FROM `{DATASET}` AS pub
  LEFT JOIN UNNEST(pub.title_localized) AS title ON title.language = '{_EN}'
  LEFT JOIN UNNEST(pub.abstract_localized) AS abstract ON abstract.language = '{_EN}'
"""

# Default ordering: most recent publication first. The public dataset does not
# guarantee any order, so an explicit ORDER BY keeps dry-runs reproducible.
_ORDER = "ORDER BY pub.publication_date DESC"

_LIMIT_RE = re.compile(r"\blimit\s+\d+\s*$", re.IGNORECASE)

# publication_number format in the dataset is hyphenated: CC-NNNNNNN-K
# (e.g. "US-6506148-B2"). Accept both the compact form ("US6506148B2") and the
# hyphenated form, and produce the dataset's canonical format.
_PUB_COMPACT = re.compile(r"^([A-Z]{2})(\d{6,12})([A-Z]\d?)?$", re.IGNORECASE)


def normalize_publication_number(pub_number: str) -> str:
    """Return the dataset's canonical ``CC-NNNNNNN-K`` form, or a LIKE pattern.

    Accepts ``"US6506148B2"``, ``"US-6506148-B2"``, ``"us6506148b2"``, and
    kind-less ``"US6506148"``.

    With a kind code → canonical hyphenated form for exact ``=`` matching:
        "US6506148B2"  ->  "US-6506148-B2"
    Without a kind code → LIKE pattern matching every kind of that number:
        "US6506148"    ->  "US-6506148-%"

    Raises ``ValueError`` for unparseable input.
    """
    s = re.sub(r"[^A-Za-z0-9]", "", pub_number.strip())
    m = _PUB_COMPACT.match(s)
    if not m:
        raise ValueError(f"unparseable publication number: {pub_number!r}")
    cc, num = m.group(1).upper(), m.group(2)
    kind = (m.group(3) or "").upper()
    if kind:
        return f"{cc}-{num}-{kind}"
    return f"{cc}-{num}-%"


def _int_date_to_iso(value: Any) -> str | None:
    """Convert BigQuery INT64 YYYYMMDD dates to ISO 'YYYY-MM-DD' (or None)."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    if v <= 0 or v < 10000000:
        return None
    s = f"{v:08d}"
    return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"


class BigQueryUnavailable(RuntimeError):
    """Raised when BigQuery cannot be used (missing lib, no credentials, or a
    non-retryable configuration error). Callers should fall back to the HTTP
    live-adapter path."""


def _load_env(path: str | None = None) -> dict[str, str]:
    """Minimal KEY=VALUE .env loader (mirrors engine_v17.epo_ops.config.load_env)
    so the adapter can read GOOGLE_APPLICATION_CREDENTIALS / GCP_PROJECT_ID from
    a local .env without requiring python-dotenv."""
    env: dict[str, str] = {}
    candidates = [
        path,
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    for cand in candidates:
        if not cand or not os.path.isfile(cand):
            continue
        with open(cand, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
                env[key] = env.get(key, value)
        break
    return env


def client_factory():
    """Return a configured ``google.cloud.bigquery.Client`` or raise
    ``BigQueryUnavailable``.

    Safe to call repeatedly; reads credentials from the environment
    (``GOOGLE_APPLICATION_CREDENTIALS``) and ``GCP_PROJECT_ID`` (falling back to
    the application default credential chain). Never raises a raw ImportError or
    default-credentials error out of the module — those are converted to
    ``BigQueryUnavailable``.
    """
    try:
        from google.cloud import bigquery  # type: ignore
    except Exception as exc:  # pragma: no cover - env dependent
        raise BigQueryUnavailable(f"google-cloud-bigquery not installed: {exc}") from exc

    _load_env()

    project = os.environ.get("GCP_PROJECT_ID", "").strip() or None

    # Explicitly honour GOOGLE_APPLICATION_CREDENTIALS if provided so the service
    # account is used even if it is not the app-default account.
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    try:
        if creds_path and os.path.isfile(creds_path):
            client = bigquery.Client(project=project, credentials=None)
            # Point google-auth at the explicit file by re-creating with a
            # credentials object loaded from the file.
            from google.oauth2 import service_account  # type: ignore

            credentials = service_account.Credentials.from_service_account_file(
                creds_path
            )
            client = bigquery.Client(project=project, credentials=credentials)
        else:
            client = bigquery.Client(project=project)
    except Exception as exc:  # pragma: no cover - env dependent
        raise BigQueryUnavailable(
            f"Could not initialise BigQuery client: {exc}. "
            "Set GOOGLE_APPLICATION_CREDENTIALS / GCP_PROJECT_ID or use the "
            "application-default credential chain."
        ) from exc

    return client


def _safe_query(client, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a query, converting BigQuery/credential errors to BigQueryUnavailable."""
    try:
        job = client.query(query, job_config=None)
        rows = job.result()
        return [dict(row.items()) for row in rows]
    except Exception as exc:  # pragma: no cover - env dependent
        # Quota / permission / rate errors are non-retryable for an offline
        # adapter; surface them so callers can fall back to HTTP.
        raise BigQueryUnavailable(f"BigQuery query failed: {exc}") from exc


def _rows_to_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map flat query rows onto the downstream record schema.

    The pipeline's landscape normaliser reads ``publication_number``,
    ``family_id``, ``assignee`` and ``relevance``; the metadata reader reads
    ``title``, ``publication_date``, ``backward_references``,
    ``forward_references``. Unavailable fields are omitted (never invented).
    BigQuery INT64 YYYYMMDD dates are converted to ISO strings; ARRAY<STRUCT>
    classification columns are flattened to plain code lists.
    """
    records: list[dict[str, Any]] = []
    for row in rows:
        record: dict[str, Any] = {}
        pub = (row.get("publication_number") or "").strip()
        if pub:
            record["publication_number"] = pub
            record["family_id"] = row.get("family_id") or pub
        grant = _int_date_to_iso(row.get("grant_date"))
        if grant:
            record["grant_date"] = grant
        pubd = _int_date_to_iso(row.get("publication_date"))
        if pubd:
            record["publication_date"] = pubd
        if row.get("title"):
            record["title"] = row["title"]
        if row.get("abstract_text"):
            record["abstract"] = row["abstract_text"]
        cpc = _struct_codes(row.get("cpc_codes"))
        if cpc:
            record["cpc"] = cpc
        ipc = _struct_codes(row.get("ipc_codes"))
        if ipc:
            record["ipc"] = ipc
        if row.get("assignee"):
            record["assignee"] = row["assignee"]
        # Downstream landscape normaliser uses this default; we never claim
        # relevance we did not compute.
        record["relevance"] = {"direct": False, "adjacent": True, "contextual": False, "decision_value": "low"}
        records.append(record)
    return records


def _struct_codes(value: Any) -> list[str]:
    """Flatten an ARRAY<STRUCT<code STRING,...>> (or plain string list) to
    de-duplicated codes, preserving order."""
    out: list[str] = []
    if not value:
        return out
    for item in value:
        if isinstance(item, dict):
            code = item.get("code")
        elif isinstance(item, str):
            code = item
        else:
            # Row/Struct object: try attribute then item access.
            code = getattr(item, "code", None)
            if code is None and hasattr(item, "get"):
                code = item.get("code")
        if code and str(code) not in out:
            out.append(str(code))
    return out


def _keyword_sql(keywords: list[str]) -> str:
    """Build a conjunction of LIKE conditions over the flattened English
    title/abstract. Returns a bare predicate (no leading ``AND``) so it can be
    composed with any supplementary WHERE conditions."""
    terms = [k.strip() for k in keywords if k and k.strip()]
    if not terms:
        raise ValueError("search_patents_by_keywords requires at least one keyword")
    clauses = []
    for term in terms:
        esc = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        clause = "(LOWER(title.text) LIKE LOWER('%" + esc + "%') OR LOWER(abstract.text) LIKE LOWER('%" + esc + "%'))"
        clauses.append(clause)
    return "(" + ") AND (".join(clauses) + ")" if len(clauses) > 1 else clauses[0]


def _apply_limit(sql: str, limit: int) -> str:
    """Append a LIMIT clause, replacing any existing trailing LIMIT (defensive)."""
    sql = _LIMIT_RE.sub("", sql).rstrip()
    return f"{sql}\nLIMIT {int(limit)}"


def search_patents_by_keywords(
    keywords: list[str],
    start_date: int | None = None,
    limit: int = 100,
    *,
    _client=None,
) -> list[dict[str, Any]]:
    """Return publications whose English title/abstract contains ALL keywords.

    Args:
        keywords: non-empty list of terms (matched case-insensitively as a
            conjunction, i.e. every term must appear).
        start_date: optional ISO year (e.g. 2001) — filters to publications on or
            after that year's start. Provided as ``int`` per the interface.
        limit: max rows (default 100).

    Returns:
        ``list[dict]`` matching the downstream record schema.
    """
    if _client is None:
        client = client_factory()
    else:
        client = _client
    where = _keyword_sql(keywords)
    if start_date is not None:
        # publication_date is INT64 YYYYMMDD — filter with the same integer shape.
        where += f" AND pub.publication_date >= {int(start_date) * 10000 + 101}"
    sql = f"{_SELECT} WHERE {where} {_ORDER}"
    sql = _apply_limit(sql, limit)
    return _rows_to_records(_safe_query(client, sql))


def search_patents_by_cpc(
    cpc_prefix: str,
    keywords: list[str] | None = None,
    limit: int = 100,
    *,
    _client=None,
) -> list[dict[str, Any]]:
    """Return publications whose CPC code starts with ``cpc_prefix``.

    If ``keywords`` is provided, additionally requiring every keyword in the
    English title/abstract (narrowing the classification search to relevant
    subject matter).

    Args:
        cpc_prefix: e.g. ``"A61N2"``.
        keywords: optional list of terms to require in title/abstract.
        limit: max rows (default 100).
    """
    if not cpc_prefix or not cpc_prefix.strip():
        raise ValueError("search_patents_by_cpc requires a non-empty cpc_prefix")
    client = client_factory() if _client is None else _client
    prefix = cpc_prefix.strip()
    where = f"EXISTS (SELECT 1 FROM UNNEST(pub.cpc) AS c WHERE c.code LIKE '{prefix}%')"
    if keywords:
        where += " AND " + _keyword_sql(keywords)
    sql = f"{_SELECT} WHERE {where} {_ORDER}"
    sql = _apply_limit(sql, limit)
    return _rows_to_records(_safe_query(client, sql))


def get_patent_by_publication_number(pub_number: str, *, _client=None) -> dict[str, Any]:
    """Return a single publication record keyed by publication number.

    Args:
        pub_number: e.g. ``"US6506148B2"`` or ``"US6506148"``.

    Returns:
        a record ``dict`` (empty ``dict`` if not found).
    """
    if not pub_number or not pub_number.strip():
        raise ValueError("get_patent_by_publication_number requires a publication number")
    client = client_factory() if _client is None else _client
    normalized = normalize_publication_number(pub_number)
    sql = (
        f"{_SELECT} WHERE pub.publication_number LIKE '{normalized}' "
        f"{_ORDER} LIMIT 1"
    )
    rows = _safe_query(client, sql)
    records = _rows_to_records(rows)
    return records[0] if records else {}
