"""EPO OPS citation retrieval — patcit and nplcit from bibliographic data."""

from __future__ import annotations

import re
from typing import Any

from .client import EpoOpsClient
from .models import CitationBundle, NplEvidenceRecord
from .parser import parse_bibliographic_xml


def normalize_patent_number(patent_id: str) -> str:
    """
    Normalize a patent ID to EPO OPS dotted publication format.

    OPS v3.2 data endpoints require dot-separated components
    (CC.NUMBER[.KIND]); compact forms such as "US5215088A" return 404.

    Examples:
        US5215088  -> US.5215088
        US5215088A -> US.5215088.A
        US8527057B2 -> US.8527057.B2
        EP1664047  -> EP.1664047
        EP1664047A1 -> EP.1664047.A1
    """
    normalized = patent_id.strip().upper()
    match = re.fullmatch(r"([A-Z]{2})(\d+)([A-Z]\d*)?", normalized)
    if not match:
        return normalized
    country, number, kind = match.groups()
    if kind:
        return f"{country}.{number}.{kind}"
    return f"{country}.{number}"


_normalize_patent_number = normalize_patent_number


def retrieve_citations(
    patent_id: str,
    client: EpoOpsClient | None = None,
    *,
    use_cache: bool = True,
) -> CitationBundle:
    """
    Retrieve all citations (patcit + nplcit) for a patent from EPO OPS.

    Uses the bibliographic data endpoint which includes the full
    citation list with category codes, origin, and phase information.

    Args:
        patent_id: Patent publication number (e.g., "US5215088", "EP1234567B1")
        client: Optional EpoOpsClient instance (creates default if not provided)
        use_cache: Whether to use cached responses

    Returns:
        CitationBundle with all patcit and nplcit entries
    """
    if client is None:
        client = EpoOpsClient()

    normalized = _normalize_patent_number(patent_id)

    # EPO OPS bibliographic data endpoint
    # We request the full document with citations
    path = f"/published-data/publication/epodoc/{normalized}/biblio"

    response = client.get(path, use_cache=use_cache)

    bundle = CitationBundle(patent_number=normalized)
    bundle.retrieval_metadata = {
        "patent_number": normalized,
        "source": "epo_ops",
        "http_status": response.get("status", 0),
        "cached": response.get("cached", False),
        "error": response.get("error"),
    }

    if response.get("status") == 200:
        xml_content = response.get("data", "")
        parsed = parse_bibliographic_xml(xml_content, normalized)
        bundle.patcit = parsed.patcit
        bundle.nplcit = parsed.nplcit
        bundle.retrieval_metadata["patcit_count"] = len(bundle.patcit)
        bundle.retrieval_metadata["nplcit_count"] = len(bundle.nplcit)
    else:
        bundle.retrieval_metadata["patcit_count"] = 0
        bundle.retrieval_metadata["nplcit_count"] = 0

    return bundle


def retrieve_npl_citations(
    patent_id: str,
    client: EpoOpsClient | None = None,
    *,
    use_cache: bool = True,
) -> list[NplEvidenceRecord]:
    """
    Retrieve only NPL citations for a patent and convert to evidence records.

    This is a convenience wrapper around retrieve_citations() that
    returns only the NPL side, normalized to NplEvidenceRecord.

    Args:
        patent_id: Patent publication number
        client: Optional EpoOpsClient instance
        use_cache: Whether to use cached responses

    Returns:
        List of NplEvidenceRecord objects with provenance preserved
    """
    bundle = retrieve_citations(patent_id, client, use_cache=use_cache)
    records = []

    for npl_cit in bundle.nplcit:
        record = NplEvidenceRecord.from_npl_citation(
            npl_cit,
            evidence_status=NplEvidenceRecord.EvidenceStatus.VERIFIED,
            retrieval_notes=[
                f"Retrieved from EPO OPS bibliographic data for {patent_id}",
                f"Cited by: {npl_cit.cited_by.value}",
                f"Phase: {npl_cit.cited_phase.value}",
                f"Categories: {[c.value for c in npl_cit.citation_categories]}",
            ],
        )
        records.append(record)

    return records