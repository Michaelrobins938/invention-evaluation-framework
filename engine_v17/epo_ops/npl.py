"""NPL/XP resolver with layered acquisition strategy.

EPO OPS does not allow direct NPL document search. Instead, the resolver:
1. Searches for patents citing the XP number via EPO OPS search
2. Retrieves bibliographic data for those patents to extract nplcit records
3. Optionally enriches NPL identity via secondary sources (Crossref, OpenAlex)

This preserves the critical provenance distinction:
    EPO says patent X cited XP123456  → PRIMARY EVIDENCE
    Crossref says XP123456 = Article Y → IDENTITY ENRICHMENT
    LLM says Article Y discusses Z     → ANALYTICAL INTERPRETATION
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote_plus

from .client import EpoOpsClient
from .models import (
    CitationBundle,
    EvidenceStatus,
    MetadataCompleteness,
    NplCitation,
    NplEvidenceRecord,
)
from .parser import parse_bibliographic_xml, parse_search_xml


@dataclass
class XpResolutionResult:
    """Result of resolving an XP document through the layered strategy."""
    xp_number: str
    records: list[NplEvidenceRecord] = field(default_factory=list)
    citing_patents_found: int = 0
    citing_patents_retrieved: int = 0
    npl_citations_extracted: int = 0
    resolution_strategy: str = "epo_ops_citing_patents"
    retrieval_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "xp_number": self.xp_number,
            "records": [r.to_dict() for r in self.records],
            "citing_patents_found": self.citing_patents_found,
            "citing_patents_retrieved": self.citing_patents_retrieved,
            "npl_citations_extracted": self.npl_citations_extracted,
            "resolution_strategy": self.resolution_strategy,
            "retrieval_notes": self.retrieval_notes,
            "metadata": self.metadata,
        }


def _normalize_xp(xp_number: str) -> str:
    """Normalize an XP number to standard format (XP followed by digits)."""
    xp_number = xp_number.strip()
    if not xp_number.upper().startswith("XP"):
        xp_number = f"XP{xp_number}"
    return xp_number.upper()


def _extract_xp_from_npl(raw_text: str) -> str | None:
    """Extract XP number from raw NPL citation text."""
    if not raw_text:
        return None
    match = re.search(r'XP\s*(\d+)', raw_text, re.IGNORECASE)
    if match:
        return f"XP{match.group(1)}".upper()
    return None


def resolve_xp_via_citing_patents(
    xp_number: str,
    client: EpoOpsClient | None = None,
    *,
    max_citing_patents: int = 5,
    use_cache: bool = True,
) -> XpResolutionResult:
    """
    Resolve an XP document by finding patents that cite it.

    This is the primary EPO OPS resolution strategy. Since XP documents
    cannot be searched directly as NPL records, we:
    1. Search for patents citing the XP number
    2. Retrieve bibliographic data for those patents
    3. Extract nplcit records that reference the XP number

    Args:
        xp_number: XP document number (e.g., "XP000123456")
        client: Optional EpoOpsClient instance
        max_citing_patents: Maximum number of citing patents to retrieve
        use_cache: Whether to use cached responses

    Returns:
        XpResolutionResult with all extracted NPL evidence records
    """
    if client is None:
        client = EpoOpsClient()

    xp = _normalize_xp(xp_number)
    result = XpResolutionResult(xp_number=xp)
    result.retrieval_notes.append(f"Strategy: EPO OPS citing-patent search for {xp}")

    # Step 1: Search for patents citing this XP number
    # EPO OPS search endpoint — query for the XP number in citation context
    search_query = f'"{xp_number}"'
    search_path = "/published-data/search"
    search_params = {
        "q": search_query,
        "range": 1,
        "end": max_citing_patents,
        "format": "json",
    }

    search_response = client.get(search_path, search_params, use_cache=use_cache)
    result.metadata["search_status"] = search_response.get("status", 0)
    result.metadata["search_cached"] = search_response.get("cached", False)

    citing_patents: list[str] = []
    if search_response.get("status") == 200:
        try:
            search_data = json.loads(search_response.get("data", "{}"))
            # Extract publication numbers from search results
            for item in search_data.get("ops:searchResult", {}).get("ops:result", []):
                doc_id = item.get("ops:publicationReference", {}).get("ops:documentId", {})
                epodoc = doc_id.get("ops:epodoc")
                if epodoc:
                    citing_patents.append(epodoc)
        except (json.JSONDecodeError, KeyError):
            result.retrieval_notes.append("Search response parsing failed — trying direct retrieval")

    result.citing_patents_found = len(citing_patents)
    result.retrieval_notes.append(
        f"Found {len(citing_patents)} potential citing patents"
    )

    # Step 2: Retrieve bibliographic data for each citing patent
    # and extract NPL citations matching our XP number
    seen_xp = set()
    for pub_number in citing_patents[:max_citing_patents]:
        try:
            bundle = retrieve_citations_for_patent(pub_number, client, use_cache=use_cache)
            result.citing_patents_retrieved += 1

            for npl_cit in bundle.nplcit:
                # Check if this NPL citation matches our XP number
                cit_xp = _extract_xp_from_npl(npl_cit.raw_citation_text or "")
                if cit_xp and cit_xp == xp:
                    if cit_xp not in seen_xp:
                        seen_xp.add(cit_xp)

                        # Determine metadata completeness
                        fields_populated = sum([
                            bool(npl_cit.title),
                            bool(npl_cit.authors),
                            bool(npl_cit.source_publication),
                            bool(npl_cit.publication_date),
                        ])

                        if fields_populated == 4:
                            mc = MetadataCompleteness.COMPLETE
                        elif fields_populated >= 2:
                            mc = MetadataCompleteness.PARTIAL
                        else:
                            mc = MetadataCompleteness.IDENTIFIER_ONLY

                        record = NplEvidenceRecord(
                            source="epo_ops",
                            citation_type="npl",
                            xp_number=cit_xp,
                            title=npl_cit.title,
                            authors=list(npl_cit.authors),
                            source_publication=npl_cit.source_publication,
                            publication_date=npl_cit.publication_date,
                            citation_categories=npl_cit.citation_categories,
                            cited_by=npl_cit.cited_by,
                            cited_phase=npl_cit.cited_phase,
                            patent_publication=npl_cit.patent_publication,
                            evidence_status=EvidenceStatus.VERIFIED,
                            metadata_completeness=mc,
                            raw_source="epo_ops",
                            retrieval_notes=[
                                f"Retrieved via EPO OPS from citing patent {pub_number}",
                                f"Original raw citation: {npl_cit.raw_citation_text}",
                            ],
                        )
                        result.records.append(record)

        except Exception as exc:
            result.retrieval_notes.append(f"Failed to retrieve {pub_number}: {exc}")

    result.npl_citations_extracted = len(result.records)

    if not result.records:
        result.retrieval_notes.append(
            f"No NPL citations for {xp} found in {result.citing_patents_retrieved} citing patents"
        )
        result.resolution_strategy = "epo_ops_no_results"

    return result


def retrieve_citations_for_patent(
    patent_id: str,
    client: EpoOpsClient | None = None,
    *,
    use_cache: bool = True,
) -> CitationBundle:
    """
    Retrieve the full citation bundle (patcit + nplcit) for a patent.

    This is the primary entry point for the EPO OPS citation layer.
    It wraps the lower-level citations.retrieve_citations() function
    and returns the full CitationBundle.

    Args:
        patent_id: Patent publication number
        client: Optional EpoOpsClient instance
        use_cache: Whether to use cached responses

    Returns:
        CitationBundle with all citations
    """
    from .citations import retrieve_citations
    return retrieve_citations(patent_id, client, use_cache=use_cache)


def build_npl_evidence_records(
    xp_number: str,
    client: EpoOpsClient | None = None,
    *,
    max_citing_patents: int = 5,
    use_cache: bool = True,
) -> list[NplEvidenceRecord]:
    """
    High-level function: resolve an XP document and return NPL evidence records.

    This is the main entry point for the NPL acquisition pipeline.
    It implements the layered strategy:

    1. EPO OPS (primary) — retrieve via citing patents
    2. If no results, note the limitation explicitly

    Secondary enrichment (Crossref, OpenAlex) should be applied by
    the caller if needed, and should be recorded as identity enrichment,
    not as primary evidence.

    Args:
        xp_number: XP document number
        client: Optional EpoOpsClient instance
        max_citing_patents: Max citing patents to examine
        use_cache: Whether to use cached responses

    Returns:
        List of NplEvidenceRecord objects
    """
    resolution = resolve_xp_via_citing_patents(
        xp_number, client,
        max_citing_patents=max_citing_patents,
        use_cache=use_cache,
    )
    return resolution.records