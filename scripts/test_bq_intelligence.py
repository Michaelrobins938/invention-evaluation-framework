#!/usr/bin/env python3
"""Verification script for the doctorate-level BigQuery patent intelligence module.

Modes (zero-cost first):
  --dry-run    validate SQL of all three strategies via BigQuery dry_run and
               print the estimated bytes each WOULD scan. No query executes,
               no billing. Requires credentials only for the dry-run estimate.
  --run        execute the strategies live (bills the project):
                 --cite  US6506148B2   (Strategy B, ~$0.10)
                 --novelty --cpc A61N2/00 --regex '\\b(sensory resonance|ptosis)\\b'
                                        (Strategy A, ~$1.50 — opt-in)
                 --moat --cpc A61N2/00 (Strategy C, ~$0.12)

Usage:
  python scripts/test_bq_intelligence.py --dry-run
  python scripts/test_bq_intelligence.py --run --cite US6506148B2
  python scripts/test_bq_intelligence.py --run --moat --cpc A61N2/00
  python scripts/test_bq_intelligence.py --run --novelty --cpc A61N2/00 \
      --regex '\\b(sensory resonance|ptosis|electromagnetic field)\\b'
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_v17 import bq_patent_intelligence as bi
from engine_v17 import bigquery_patents as bq


def _estimate(sql: str, params=None):
    """Dry-run: return estimated bytes without executing. Returns None on error."""
    from google.cloud import bigquery

    client = bi._make_client()
    job_config = bigquery.QueryJobConfig(
        dry_run=True,
        query_parameters=params or [],
    )
    try:
        job = client.query(sql, job_config=job_config)
        return job.total_bytes_processed
    except Exception as exc:
        print(f"  dry-run error: {exc}")
        return None


def _fmt_gib(n: int | None) -> str:
    return "?" if n is None else f"{n / 1024**3:,.1f} GiB (~${n / 1024**4 * 6.25:,.2f} @ $6.25/TiB)"


def dry_run(args):
    print("=== BigQuery intelligence — DRY RUN (estimates only; nothing bills) ===\n")
    print(f"Dataset: {bq.DATASET}\n")

    # Strategy A
    prefix = args.cpc if args.cpc else "A61N2/00%"
    regex = args.regex or r"\b(sensory resonance|ptosis)\b"
    sql_a = bi._STRATEGY_A_SQL.replace("@cpc_prefix", f'"{prefix}"') \
        .replace("@regex_keywords", f'"{regex}"').replace("@limit", "10")
    est_a = _estimate(sql_a)
    print(f"[A] deep_novelty_search(cpc={prefix}, regex={regex})")
    print(f"    estimated scan: {_fmt_gib(est_a)}")

    # Strategy B backward (exact pub) + forward
    sql_b = bi._BACKWARD_SQL_EQ.replace("@target", '"US-6506148-B2"').replace("@limit", "50")
    est_b = _estimate(sql_b)
    print(f"[B] citation backward (US-6506148-B2)")
    print(f"    estimated scan: {_fmt_gib(est_b)}")
    sql_f = bi._FORWARD_SQL.replace("@target", '"US-6506148-B2"').replace("@limit", "50")
    est_f = _estimate(sql_f)
    print(f"[B] citation forward (US-6506148-B2)")
    print(f"    estimated scan: {_fmt_gib(est_f)}")

    # Strategy C
    sql_c = bi._STRATEGY_C_SQL.replace("@cpc_prefix", f'"{prefix}"').replace("@limit", "20")
    est_c = _estimate(sql_c)
    print(f"[C] assignee_landscape(cpc={prefix})")
    print(f"    estimated scan: {_fmt_gib(est_c)}")

    print("\nDRY RUN complete — no query executed.")
    return 0


def run(args):
    print("=== BigQuery intelligence — LIVE RUN (bills the project) ===\n")
    did = False
    if args.cite:
        did = True
        tree = bi.get_citation_tree(args.cite, depth=args.depth, limit=args.limit)
        print(f"[B] citation tree for {tree.focal}")
        print(f"    backward: {len(tree.backward())} | forward: {len(tree.forward())}")
        for n in tree.backward()[:10]:
            print(f"      B {n.publication_number:20} cat={n.category}")
        for n in tree.forward()[:10]:
            print(f"      F {n.publication_number:20} cat={n.category}")
    if args.novelty:
        did = True
        prefix = args.cpc or "A61N2/00"
        recs = bi.deep_novelty_search(prefix, args.regex or r"\b(sensory resonance|ptosis)\b",
                                      limit=args.limit, max_bytes=args.authorize_bytes)
        print(f"[A] deep novelty cpc={prefix} regex={args.regex} -> {len(recs)} records")
        for r in recs[:10]:
            print(f"      {r.get('publication_number'):18} prio={r.get('priority_date')} | {(r.get('title') or '')[:55]}")
    if args.moat:
        did = True
        prefix = args.cpc or "A61N2/00"
        rows = bi.assignee_landscape(prefix, limit=args.limit, max_bytes=args.authorize_bytes)
        print(f"[C] assignee moat cpc={prefix} -> {len(rows)} assignees")
        for r in rows[:10]:
            print(f"      {r['assignee']:40} families={r['total_patent_families']} earliest={r['earliest_priority']}")
    if args.fulltext:
        did = True
        out = bi.get_patent_full_text(args.fulltext)
        print(f"[full-text] {args.fulltext}:")
        for k, v in out.items():
            print(f"      {k}: {str(v)[:80]}")
    if not did:
        print("no action selected; use --cite / --novelty / --moat / --fulltext")
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="estimate costs without executing (default)")
    ap.add_argument("--run", action="store_true", help="execute live queries")
    ap.add_argument("--cite", default=None, help="publication number for citation tree (Strategy B)")
    ap.add_argument("--novelty", action="store_true", help="run deep novelty search (Strategy A)")
    ap.add_argument("--moat", action="store_true", help="run assignee landscape (Strategy C)")
    ap.add_argument("--fulltext", default=None, help="publication number for claims/description full text")
    ap.add_argument("--cpc", default=None, help="CPC prefix, e.g. A61N2/00")
    ap.add_argument("--regex", default=None, help="RE2 regex over abstracts (Strategy A)")
    ap.add_argument("--depth", type=int, default=1, help="citation tree depth (Strategy B)")
    ap.add_argument("--limit", type=int, default=50, help="row limit")
    ap.add_argument("--authorize-bytes", type=int, default=None,
                    help="explicit opt-in byte ceiling for broad scans (e.g. 250000000000 for Strategy A)")
    args = ap.parse_args()
    if args.run:
        return run(args)
    return dry_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
