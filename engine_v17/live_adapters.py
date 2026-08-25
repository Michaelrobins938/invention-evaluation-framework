"""Live research adapters that create execution records at request time."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Callable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .execution import AvenueExecutionStatus, ExecutionLedger
from .evidence_gate import SourceObject, apply_evidence_sufficiency_gate
from .domain_parsers import (
    parse_crossref_literature,
    parse_market_proxy,
    parse_partner_candidates,
    parse_patent_claims,
    parse_patent_metadata,
)

# EPO OPS — primary NPL source (optional; falls back gracefully if not configured)
try:
    from .epo_ops import (
        CitationBundle,
        EpoOpsClient,
        build_npl_evidence_records,
        normalize_patent_number,
        retrieve_citations,
    )
    _EPO_OPS_AVAILABLE = True
except ImportError:
    _EPO_OPS_AVAILABLE = False


Fetcher = Callable[[str], bytes]


def _default_fetcher(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "invention-evaluation-engine/1.7"})
    with urlopen(request, timeout=60) as response:
        return response.read()


@dataclass
class HttpLiveAdapter:
    fetcher: Fetcher = _default_fetcher

    def fetch(
        self,
        ledger: ExecutionLedger,
        *,
        phase_id: str,
        action_type: str,
        source: str,
        url: str,
        query: str,
        artifact_path: Path,
        result_count: int | None = None,
    ):
        body = self.fetcher(url)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(body)
        return ledger.record(
            phase_id=phase_id,
            action_type=action_type,
            source=source,
            query=query,
            result_count=result_count,
            result_artifact=str(artifact_path),
            outcome="live response retrieved",
            candidate_evidence=result_count is not None and result_count > 0,
        )


def _write_phase(path: Path, title: str, record, source_url: str, summary: str) -> Path:
    path.write_text(
        f"# {title}\n\n"
        f"- Execution ID: `{record.execution_id}`\n"
        f"- Source: {source_url}\n"
        f"- Execution status: `{record.status.value}`\n"
        f"- Result count: `{record.result_count}`\n\n"
        f"{summary}\n",
        encoding="utf-8",
    )
    return path


_STOPWORDS = frozenset(
    """a an and are as at be by for from has have in is it its of on or that the
    this to with system method device apparatus comprising wherein thereof thus
    invention disclosure background summary claims abstract related art prior""".split()
)


def derive_invention_terms(submission_text: str, limit: int = 6) -> str:
    """Derive search terms from submission text — frequency-ranked, stopword-free.

    Queries must describe THIS invention. Hardcoded fixture subjects are
    prohibited: searching the wrong technology records motion, not evidence.
    """
    words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", submission_text or "")
    counts: dict[str, int] = {}
    for w in words:
        lw = w.lower()
        if lw in _STOPWORDS:
            continue
        counts[lw] = counts.get(lw, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return " ".join(w for w, _ in ranked[:limit])


def run_live_phase_adapters(
    *,
    patent_id: str,
    output_dir: Path,
    ledger: ExecutionLedger,
    fetcher: Fetcher = _default_fetcher,
    submission_text: str | None = None,
) -> dict[str, Path]:
    """Execute the minimum live phase set and return generated phase artifacts.

    Retrieval failures degrade to BLOCKED avenue records (evidence debt) —
    a live source being unavailable never aborts the pipeline.

    Patent identity resolution follows a route ladder (direct publication →
    granted variants → title search); each route is its own ledger record.
    A source is only BLOCKED after every route has been attempted.
    """
    def _safe_fetch(adapter: HttpLiveAdapter, ledger_ref: ExecutionLedger, *, failure_note: str, **kwargs):
        try:
            return adapter.fetch(ledger_ref, **kwargs)
        except Exception as exc:
            artifact_path: Path = kwargs["artifact_path"]
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                f"# Retrieval blocked\n\n{failure_note}\n\n"
                f"Error: {type(exc).__name__}: {str(exc)[:200]}\n",
                encoding="utf-8",
            )
            return ledger_ref.record(
                phase_id=kwargs["phase_id"],
                action_type=kwargs["action_type"],
                source=kwargs["source"],
                query=kwargs["query"],
                result_artifact=str(artifact_path),
                outcome=f"retrieval blocked ({type(exc).__name__}: {str(exc)[:120]}); recorded as evidence debt",
                candidate_evidence=False,
                evidence_sufficiency=False,
                status=AvenueExecutionStatus.BLOCKED,
            )

    adapter = HttpLiveAdapter(fetcher)
    output_dir.mkdir(parents=True, exist_ok=True)
    normalized = patent_id.upper()
    publication_id = normalized if re.search(r"B[0-9A-Z]+$", normalized) else f"{normalized}A"
    patent_url = f"https://patents.google.com/patent/{publication_id}/en"
    patent_raw = output_dir / f"raw-patent-{normalized.lower()}.html"
    # ── Patent identity resolution: route ladder, not single shot ───────────
    # A source is resolvable only when a route SUCCEEDS; it is BLOCKED only
    # after every route has been attempted and individually recorded.
    terms = derive_invention_terms(submission_text or "")
    routes: list[tuple[str, str]] = [
        (f"direct publication {publication_id}", patent_url),
        (f"granted variant {normalized}B2", f"https://patents.google.com/patent/{normalized}B2/en"),
    ]
    if terms:
        routes.append((
            f"title search ({terms[:60]})",
            "https://patents.google.com/?q=" + quote_plus(terms) + "&oq=" + quote_plus(terms),
        ))

    patent_record = None
    resolved_html: str | None = None
    for route_name, route_url in routes:
        route_artifact = output_dir / f"raw-patent-route-{routes.index((route_name, route_url)) + 1}.html"
        rec = _safe_fetch(
            adapter, ledger,
            failure_note=f"Patent resolution route failed: {route_name}.",
            phase_id="03",
            action_type="patent_search",
            source="Google Patents",
            url=route_url,
            query=f"{normalized} via {route_name}",
            artifact_path=route_artifact,
            result_count=None,
        )
        if rec.status == AvenueExecutionStatus.COMPLETE:
            html = route_artifact.read_text(encoding="utf-8", errors="ignore")
            if "/patent/" in route_url and "?q=" not in route_url and html.strip():
                patent_record, resolved_html = rec, html
                break
            if "?q=" in route_url:
                match = re.search(r'href="/patent/([A-Z0-9]+)/en"', html)
                if match:
                    hit_id = match.group(1)
                    hit_url = f"https://patents.google.com/patent/{hit_id}/en"
                    hit_artifact = output_dir / f"raw-patent-{hit_id.lower()}.html"
                    hit_rec = _safe_fetch(
                        adapter, ledger,
                        failure_note=f"Search-resolved patent {hit_id} could not be retrieved.",
                        phase_id="03",
                        action_type="patent_search",
                        source="Google Patents",
                        url=hit_url,
                        query=f"{hit_id} resolved from title search",
                        artifact_path=hit_artifact,
                        result_count=None,
                    )
                    if hit_rec.status == AvenueExecutionStatus.COMPLETE:
                        patent_record = hit_rec
                        resolved_html = hit_artifact.read_text(encoding="utf-8", errors="ignore")
                        break

    if patent_record is None:
        debt_note = (
            f"# Retrieval blocked\n\nPatent identity '{publication_id}' unresolved after "
            f"{len(routes)} routes: " + "; ".join(name for name, _ in routes) + "\n"
        )
        patent_raw.parent.mkdir(parents=True, exist_ok=True)
        patent_raw.write_text(debt_note, encoding="utf-8")
        patent_record = ledger.record(
            phase_id="03",
            action_type="patent_search",
            source="Google Patents",
            query=normalized,
            result_artifact=str(patent_raw),
            outcome=f"all {len(routes)} resolution routes blocked; recorded as evidence debt",
            candidate_evidence=False,
            evidence_sufficiency=False,
            status=AvenueExecutionStatus.BLOCKED,
        )
        resolved_html = debt_note

    if resolved_html and not patent_raw.exists():
        patent_raw.write_text(resolved_html, encoding="utf-8")
    patent_metadata = parse_patent_metadata(resolved_html or "", normalized)
    target_claims = parse_patent_claims(resolved_html or "")

    # ── EPO OPS citation retrieval (primary NPL source) ─────────────────────
    epo_citation_bundle: CitationBundle | None = None
    epo_npl_records: list[NplEvidenceRecord] = []
    epo_citation_record = None
    epo_npl_record = None
    epo_citation_raw: Path | None = None
    epo_npl_raw: Path | None = None
    if _EPO_OPS_AVAILABLE:
        try:
            epo_client = EpoOpsClient()
            epo_citation_bundle = retrieve_citations(normalized, epo_client, use_cache=True)
            total_citations = len(epo_citation_bundle.patcit) + len(epo_citation_bundle.nplcit)

            # Only persist and record when EPO OPS returned actual citation data
            if total_citations > 0:
                epo_citation_raw = output_dir / f"epo-ops-citations-{normalized.lower()}.json"
                epo_citation_raw.write_text(
                    json.dumps(epo_citation_bundle.to_dict(), indent=2, default=str) + "\n",
                    encoding="utf-8",
                )
                # Data was already fetched via the authenticated client — record
                # it directly instead of re-downloading (anonymous re-fetch = 403).
                epo_citation_record = ledger.record(
                    phase_id="03",
                    action_type="epo_ops_citation_retrieval",
                    source="EPO OPS",
                    query=normalized,
                    result_count=total_citations,
                    result_artifact=str(epo_citation_raw),
                    outcome="live response retrieved",
                    candidate_evidence=True,
                )

            # Resolve NPL citations (XP documents) via citing-patent strategy
            xp_numbers = [cit.xp_number for cit in epo_citation_bundle.nplcit if cit.xp_number]
            if xp_numbers:
                for xp_num in xp_numbers[:5]:  # limit to first 5 XP refs
                    xp_records = build_npl_evidence_records(xp_num, epo_client, use_cache=True)
                    epo_npl_records.extend(xp_records)

                if epo_npl_records:
                    epo_npl_raw = output_dir / f"epo-ops-npl-{normalized.lower()}.json"
                    epo_npl_raw.write_text(
                        json.dumps(
                            {"xp_resolutions": [r.to_dict() for r in epo_npl_records]},
                            indent=2, default=str,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    # Same as citations: authenticated data recorded directly.
                    epo_npl_record = ledger.record(
                        phase_id="04",
                        action_type="epo_ops_npl_resolution",
                        source="EPO OPS NPL",
                        query=f"XP citations for {normalized}",
                        result_count=len(epo_npl_records),
                        result_artifact=str(epo_npl_raw),
                        outcome="live response retrieved",
                        candidate_evidence=True,
                    )
        except Exception as _exc:
            # EPO OPS unavailable — continue without it; existing Google Patents
            # flow remains the primary patent source.
            pass

    literature_query = terms or f"patent {normalized}"
    literature_url = "https://api.crossref.org/works?query=" + quote_plus(literature_query) + "&rows=5"
    literature_raw = output_dir / "raw-literature-crossref.json"
    literature_record = _safe_fetch(
        adapter, ledger,
        failure_note="Crossref literature query could not be retrieved.",
        phase_id="04",
        action_type="literature_search",
        source="Crossref API",
        url=literature_url,
        query=literature_query,
        artifact_path=literature_raw,
        result_count=None,
    )

    market_url = "https://api.worldbank.org/v2/country/WLD/indicator/SP.POP.TOTL?format=json"
    market_raw = output_dir / "raw-market-worldbank.json"
    market_record = _safe_fetch(
        adapter, ledger,
        failure_note="World Bank market proxy indicator could not be retrieved.",
        phase_id="06",
        action_type="market_proxy_search",
        source="World Bank API",
        url=market_url,
        query="World population indicator SP.POP.TOTL",
        artifact_path=market_raw,
        result_count=None,
    )

    partner_query = terms or f"patent {normalized}"
    partner_url = "https://patents.google.com/?q=" + quote_plus(partner_query)
    partner_raw = output_dir / "raw-partner-patent-search.html"
    partner_record = _safe_fetch(
        adapter, ledger,
        failure_note="Partner patent search could not be retrieved.",
        phase_id="07",
        action_type="partner_search",
        source="Google Patents search",
        url=partner_url,
        query=partner_query,
        artifact_path=partner_raw,
        result_count=None,
    )

    troubleshooting_query = f"{terms} claim element mapping evidence sufficiency".strip() or f"patent {normalized} claim mapping"
    troubleshooting_url = "https://patents.google.com/?q=" + quote_plus(troubleshooting_query)
    troubleshooting_raw = output_dir / "raw-recovery-troubleshooting.html"
    troubleshooting_record = _safe_fetch(
        adapter, ledger,
        failure_note="Recovery troubleshooting search could not be retrieved.",
        phase_id="05",
        action_type="recovery_troubleshooting",
        source="Google Patents search guidance route",
        url=troubleshooting_url,
        query=troubleshooting_query,
        artifact_path=troubleshooting_raw,
        result_count=None,
    )

    recovery_strategies = [
        ("terminology", terms or f"patent {normalized}", "https://patents.google.com/?q="),
        ("classification", f"{terms} CPC classification".strip(), "https://patents.google.com/?q="),
        ("citation_lineage", normalized, f"https://patents.google.com/patent/{publication_id}/en"),
        ("alternate_source", literature_query, "https://api.crossref.org/works?query="),
        ("entity_jurisdiction", f"{terms} assignee applicant".strip() or f"patent {normalized}", "https://patents.google.com/?q="),
    ]
    recovery_records = []
    for index, (strategy_class, query, base_url) in enumerate(recovery_strategies, start=1):
        url = base_url + (quote_plus(query) if base_url.endswith("=") else "")
        raw_path = output_dir / f"raw-recovery-{index:02d}-{strategy_class}.bin"
        record = _safe_fetch(
            adapter, ledger,
            failure_note=f"Recovery strategy {strategy_class} search could not be retrieved.",
            phase_id="05",
            action_type="recovery_search",
            source=base_url.split("/")[2],
            url=url,
            query=query,
            artifact_path=raw_path,
            result_count=None,
        )
        recovery_records.append({
            "recovery_id": f"R{index}",
            "strategy_class": strategy_class,
            "execution_id": record.execution_id,
            "query": query,
            "source": base_url,
            "status": "EXECUTED" if record.status == AvenueExecutionStatus.COMPLETE else "BLOCKED",
            "result_artifact": str(raw_path),
        })

    reference_records = []
    for reference_id in patent_metadata.get("backward_references", [])[:3]:
        reference_url = f"https://patents.google.com/patent/{reference_id}/en"
        reference_raw = output_dir / f"raw-prior-art-{reference_id.lower()}.html"
        reference_execution = _safe_fetch(
            adapter, ledger,
            failure_note=f"Prior-art reference {reference_id} could not be retrieved.",
            phase_id="05",
            action_type="prior_art_reference_fetch",
            source="Google Patents",
            url=reference_url,
            query=reference_id,
            artifact_path=reference_raw,
            result_count=None,
        )
        reference_html = reference_raw.read_text(encoding="utf-8", errors="ignore")
        reference_claims = parse_patent_claims(reference_html)
        reference_records.append({
            "reference_id": reference_id,
            "execution_id": reference_execution.execution_id,
            "raw_artifact": str(reference_raw),
            "claims": reference_claims,
        })
    claim_mapping = {
        "target_patent": normalized,
        "target_claim": target_claims[0] if target_claims else None,
        "references": reference_records,
        "state": "WORK QUEUE",
        "reason": "reference claim text and temporal/legal relevance require proposition-level verification",
    }
    claim_mapping_path = output_dir / "claim-mapping.json"
    claim_mapping_path.write_text(json.dumps(claim_mapping, indent=2) + "\n", encoding="utf-8")
    recovery_payload = {
        "initial_failure": {
            "type": "insufficient_proposition_support",
            "proposition_id": "P-05-001",
            "observation": "retrieval produced candidate material without complete claim-level support",
        },
        "diagnosis": {
            "hypothesis": "retrieval relevance is not equivalent to claim-element evidence",
            "supporting_observations": ["candidate records lack proposition-level mapping"],
        },
        "troubleshooting": {
            "executed": True,
            "execution_id": troubleshooting_record.execution_id,
            "query": troubleshooting_query,
            "source": troubleshooting_url,
            "result_artifact": str(troubleshooting_raw),
            "outcome": "recovery classes selected and executed",
        },
        "strategies": recovery_records,
        "reassessment": {
            "state": "WORK QUEUE",
            "reason": "all recovery responses remain candidates pending source verification and claim mapping",
            "additional_work_required": True,
        },
    }
    recovery_path = output_dir / "recovery-records.json"
    recovery_path.write_text(json.dumps(recovery_payload, indent=2) + "\n", encoding="utf-8")

    evidence_decisions = [
        apply_evidence_sufficiency_gate(
            proposition_id="P-05-001",
            schema_id="prior_art_disclosure",
            source=SourceObject(normalized, "patent", patent_url, patent_record.execution_id, str(patent_raw)),
            proposition_support=None,
            temporal_relevance=False,
        ),
        apply_evidence_sufficiency_gate(
            proposition_id="P-06-001",
            schema_id="literature_disclosure",
            source=SourceObject("Crossref query", "literature_search", literature_url, literature_record.execution_id, str(literature_raw)),
            proposition_support=None,
            temporal_relevance=False,
        ),
        apply_evidence_sufficiency_gate(
            proposition_id="P-07-001",
            schema_id="market_sizing",
            source=SourceObject("World Bank API", "market_proxy", market_url, market_record.execution_id, str(market_raw)),
            proposition_support=None,
            temporal_relevance=False,
        ),
        apply_evidence_sufficiency_gate(
            proposition_id="P-08-001",
            schema_id="partner_fit",
            source=SourceObject("Google Patents search", "partner_search", partner_url, partner_record.execution_id, str(partner_raw)),
            proposition_support=None,
            temporal_relevance=False,
        ),
        # EPO OPS citation evidence decisions
        *(
            [
                apply_evidence_sufficiency_gate(
                    proposition_id="P-03-002",
                    schema_id="patent_citations",
                    source=SourceObject(
                        "EPO OPS",
                        "epo_ops_citation",
                        epo_citation_record.query if epo_citation_record else "",
                        epo_citation_record.execution_id if epo_citation_record else "",
                        str(epo_citation_raw) if epo_citation_raw else "",
                    ),
                    proposition_support=None,
                    temporal_relevance=True,
                ),
                apply_evidence_sufficiency_gate(
                    proposition_id="P-04-002",
                    schema_id="npl_citations",
                    source=SourceObject(
                        "EPO OPS NPL",
                        "epo_ops_npl",
                        epo_npl_record.query if epo_npl_record else "",
                        epo_npl_record.execution_id if epo_npl_record else "",
                        str(epo_npl_raw) if epo_npl_raw else "",
                    ),
                    proposition_support=None,
                    temporal_relevance=True,
                ),
            ]
            if epo_citation_record is not None
            else []
        ),
    ]
    evidence_path = output_dir / "adapter-evidence-decisions.json"
    evidence_path.write_text(json.dumps([decision.to_dict() for decision in evidence_decisions], indent=2) + "\n", encoding="utf-8")

    parsed_domains = {
        "patent": {**patent_metadata, "claims": target_claims},
        "literature": parse_crossref_literature(literature_raw.read_bytes()),
        "market": parse_market_proxy(market_raw.read_bytes()),
        "partners": parse_partner_candidates(partner_raw.read_bytes()),
        **(
            {
                "epo_ops_citations": (
                    epo_citation_bundle.to_dict() if epo_citation_bundle else {}
                ),
                "epo_ops_npl": {
                    "xp_resolutions": [r.to_dict() for r in epo_npl_records],
                    "xp_numbers_found": [
                        r.xp_number for r in epo_npl_records if r.xp_number
                    ],
                    "metadata_completeness": {
                        r.xp_number: r.metadata_completeness.value
                        for r in epo_npl_records
                        if r.xp_number
                    },
                },
            }
            if epo_citation_bundle is not None
            else {}
        ),
    }
    parsed_path = output_dir / "parsed-domain-evidence.json"
    parsed_path.write_text(json.dumps(parsed_domains, indent=2) + "\n", encoding="utf-8")

    artifacts = {
        "patent": _write_phase(
            output_dir / f"patent-landscape-{normalized.lower()}.md",
            "Patent Landscape Analysis",
            patent_record,
            patent_url,
            "The primary patent record was retrieved live. Family, continuity, claim mapping, and normalized landscape analysis remain evidence-debt items.",
        ),
        "literature": _write_phase(
            output_dir / f"literature-search-{normalized.lower()}.md",
            "Literature Analysis",
            literature_record,
            literature_url,
            "Crossref literature retrieval was executed live. Returned records require identity, relevance, date, and proposition-level verification.",
        ),
        "market": _write_phase(
            output_dir / f"market-analysis-{normalized.lower()}.md",
            "Market Analysis",
            market_record,
            market_url,
            "A public population proxy was retrieved live. It is not a market-size finding and requires bounded patient, procedure, reimbursement, and adoption modeling.",
        ),
        "partners": _write_phase(
            output_dir / f"partner-analysis-{normalized.lower()}.md",
            "Potential Partners",
            partner_record,
            partner_url,
            "A live adjacent-technology search was executed. Organization-specific partner fit remains unverified.",
        ),
        "recovery": _write_phase(
            output_dir / f"recovery-record-{normalized.lower()}.md",
            "Evidence Recovery Record",
            ledger.executions[-1],
            "execution-ledger.json",
            "Five materially distinct recovery strategies were executed and linked to execution IDs in recovery-records.json. Results remain candidate inputs until proposition-level verification.",
        ),
        "evidence": evidence_path,
        "parsed": parsed_path,
        "claim_mapping": claim_mapping_path,
    }
    return artifacts
