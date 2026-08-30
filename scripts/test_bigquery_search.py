#!/usr/bin/env python3
"""Verification script for the BigQuery Google Patents adapter.

Two modes:
  --dry-run        (default) validate SQL generation + record mapping without
                   querying BigQuery. Zero billing, no credentials required.
  --run            execute real queries against patents-public-data and print
                   results. Requires GOOGLE_APPLICATION_CREDENTIALS +
                   GCP_PROJECT_ID (and BigQuery enabled for the project).

Usage:
  python scripts/test_bigquery_search.py --dry-run
  python scripts/test_bigquery_search.py --run \
      --keywords "sensory resonance" --cpc A61N2 --pub US6506148B2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_v17 import bigquery_patents as bq


def _print_records(records, label):
    print(f"\n[{label}] {len(records)} record(s)")
    for r in records[:10]:
        pub = r.get("publication_number", "?")
        title = (r.get("title") or "")[:60]
        cpc = ",".join((r.get("cpc") or [])[:2])
        print(f"  {pub:16} {r.get('publication_date',''):10} | {cpc:16} | {title}")


def dry_run(keywords, cpc, pub):
    print("=== BigQuery adapter — DRY RUN (no query executed) ===")
    print(f"Dataset: {bq.DATASET}\n")

    # Validate SQL builders + record mapping without a live client.
    kw_sql = bq._keyword_sql(keywords or ["resonance"])
    print("keyword predicate:\n  " + kw_sql + "\n")

    select = "SELECT * FROM (" + bq._SELECT + ")"
    sql_kw = bq._apply_limit(select + " WHERE " + kw_sql + " " + bq._ORDER, 5)
    print("search_patents_by_keywords -> SQL (first 120 chars):")
    print("  " + sql_kw[:120].replace("\n", " ") + "...\n")

    if cpc:
        sql_cpc = bq._apply_limit(
            "SELECT * FROM (" + bq._SELECT + ") WHERE EXISTS ("
            "SELECT 1 FROM UNNEST(pub.cpc) AS c WHERE c.code LIKE '" + cpc + "%')"
            + (bq._keyword_sql(keywords) if keywords else "") + " " + bq._ORDER,
            5,
        )
        print("search_patents_by_cpc -> SQL (first 120 chars):")
        print("  " + sql_cpc[:120].replace("\n", " ") + "...\n")

    if pub:
        sql_pub = "SELECT * FROM (" + bq._SELECT + ") WHERE LOWER(pub.publication_number)"
        sql_pub += " = LOWER('" + pub + "') " + bq._ORDER + " LIMIT 1"
        print("get_patent_by_publication_number -> SQL:")
        print("  " + sql_pub.replace("\n", " ") + "\n")

    # record-mapping contract check
    sample = [{
        "publication_number": "US6506148B2", "grant_date": "2003-01-14",
        "title": "Nervous system manipulation", "cpc_codes": ["A61N2/00"], "ipc_codes": [],
    }]
    mapped = bq._rows_to_records(sample)
    ok_keys = {"publication_number", "family_id", "relevance"} <= set(mapped[0])
    print("record-mapping contract (landscape keys present):", "PASS" if ok_keys else "FAIL")
    print("\nDRY RUN complete — no query executed, no billing incurred.")
    return 0 if ok_keys else 1


def run(keywords, cpc, pub, limit):
    print(f"=== BigQuery adapter — LIVE RUN (queries bill the GCP project) ===")
    client = bq.client_factory()
    print("client initialised; executing...\n")

    if keywords:
        _print_records(bq.search_patents_by_keywords(keywords, limit=limit, _client=client), f"keywords={keywords}")
    if cpc:
        _print_records(bq.search_patents_by_cpc(cpc, keywords=keywords, limit=limit, _client=client), f"cpc={cpc}")
    if pub:
        rec = bq.get_patent_by_publication_number(pub, _client=client)
        if rec:
            _print_records([rec], f"publication={pub}")
        else:
            print(f"\n[{pub}] not found")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", action="store_true", help="execute real BigQuery queries")
    ap.add_argument("--dry-run", dest="dry_run", action="store_true", default=False,
                    help="validate SQL + mapping without querying (default behaviour)")
    ap.add_argument("--keywords", nargs="+", default=["sensory resonance"], help="keyword terms (conjunction)")
    ap.add_argument("--cpc", default=None, help="CPC prefix, e.g. A61N2")
    ap.add_argument("--pub", default="US6506148B2", help="publication number")
    ap.add_argument("--limit", type=int, default=50, help="max results to return (live run)")
    args = ap.parse_args()

    if args.run:
        return run(args.keywords, args.cpc, args.pub, args.limit)
    return dry_run(args.keywords, args.cpc, args.pub)


if __name__ == "__main__":
    raise SystemExit(main())
