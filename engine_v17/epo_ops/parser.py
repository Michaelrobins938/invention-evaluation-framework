"""XML parser for EPO OPS bibliographic and citation responses."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from .models import (
    CitationBundle,
    CitationCategory,
    CitedBy,
    CitedPhase,
    NplCitation,
    PatentCitation,
)

# EPO OPS XML namespaces (elements are matched by LOCAL name — OPS mixes
# the ops namespace with the default exchange namespace across endpoints)
_EPO_NS = "{http://www.epo.org/fulltext}"
_OPS_NS = "{http://ops.epo.org}"
_EXCHANGE_NS = "{http://www.epo.org/exchange}"


def _strip_namespaces(root: ET.Element) -> ET.Element:
    """Rewrite all element tags to namespace-free local names in place.

    Live OPS responses mix namespaces (ops root + exchange-ns children);
    matching on local names makes parsing robust across endpoint variants.
    """
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return root


def _text(element: ET.Element | None, tag: str, ns: str = "") -> str | None:
    """Extract text from a child element, returning None if missing."""
    if element is None:
        return None
    child = element.find(f"{ns}{tag}")
    return (child.text or "").strip() if child is not None and child.text else None


def _find_all(parent: ET.Element, tag: str, ns: str = "") -> list[ET.Element]:
    """Find all child elements with a given tag."""
    return parent.findall(f"{ns}{tag}")


def _parse_citation_category(raw: str | None) -> list[CitationCategory]:
    """Parse EPO citation category codes into enum values."""
    if not raw:
        return []
    # Map raw characters to enum members (handles SAME_FAMILY = "&")
    _CHAR_MAP = {
        "X": CitationCategory.X,
        "Y": CitationCategory.Y,
        "A": CitationCategory.A,
        "P": CitationCategory.P,
        "D": CitationCategory.D,
        "E": CitationCategory.E,
        "L": CitationCategory.L,
        "O": CitationCategory.O,
        "T": CitationCategory.T,
        "&": CitationCategory.SAME_FAMILY,
        "+": CitationCategory.PLUS,
    }
    categories = []
    for char in raw.strip():
        if char in _CHAR_MAP:
            categories.append(_CHAR_MAP[char])
    return categories


def _parse_npl_citation_text(raw_text: str) -> dict[str, Any]:
    """
    Attempt to extract structured fields from raw NPL citation text.

    EPO OPS nplcit typically contains a free-text citation like:
    "Author1; Author2. Title. Publication. Date."

    This is a best-effort parse — missing fields are expected and handled
    by metadata_completeness tracking.
    """
    result = {
        "authors": [],
        "title": None,
        "source_publication": None,
        "publication_date": None,
    }

    if not raw_text:
        return result

    text = raw_text.strip()

    # Try to split on common delimiters
    # Pattern: Authors. Title. Publication. Date.
    # Split on period+space followed by uppercase letter OR digit (for years)
    parts = re.split(r'\.\s+(?=[A-Z0-9])', text)
    # Strip trailing periods from each part
    parts = [p.strip().rstrip('.') for p in parts]

    if len(parts) >= 1:
        # First part is usually authors — split on semicolon (author separator),
        # not comma (which is part of "Last, First" name format)
        authors_raw = parts[0]
        result["authors"] = [a.strip() for a in authors_raw.split(';') if a.strip()]

    if len(parts) >= 2:
        result["title"] = parts[1].strip()

    if len(parts) >= 3:
        result["source_publication"] = parts[2].strip()

    if len(parts) >= 4:
        result["publication_date"] = parts[3].strip()

    return result


def parse_bibliographic_xml(
    xml_content: str | bytes,
    patent_number: str,
) -> CitationBundle:
    """
    Parse EPO OPS bibliographic data XML and extract all citations.

    Handles both patent citations (patcit) and non-patent literature
    citations (nplcit), preserving citation category, origin, and phase.
    """
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8", errors="replace")

    root = _strip_namespaces(ET.fromstring(xml_content))

    # Find the main document element across known OPS shapes
    doc = (
        root.find("patent-document")
        or root.find(".//exchange-document")
        or root.find("search-result")
        or root
    )

    bundle = CitationBundle(patent_number=patent_number)

    # Parse citations (biblio: bibliographic-data/references-cited; legacy: citations)
    citations_elem = doc.find("citations") or doc.find(".//references-cited")
    if citations_elem is None:
        return bundle

    for citation in _find_all(citations_elem, "citation"):
        # Determine cited-by and cited-phase from citation attributes
        cited_by_raw = citation.get("cited-by", "")
        cited_phase_raw = citation.get("cited-phase", "")

        cited_by = CitedBy.UNKNOWN
        if "examiner" in cited_by_raw.lower():
            cited_by = CitedBy.EXAMINER
        elif "applicant" in cited_by_raw.lower():
            cited_by = CitedBy.APPLICANT
        elif "third" in cited_by_raw.lower():
            cited_by = CitedBy.THIRD_PARTY

        cited_phase = CitedPhase.UNKNOWN
        if "search" in cited_phase_raw.lower():
            cited_phase = CitedPhase.SEARCH
        elif "examination" in cited_phase_raw.lower():
            cited_phase = CitedPhase.EXAMINATION
        elif "opposition" in cited_phase_raw.lower():
            cited_phase = CitedPhase.OPPOSITION
        elif "appeal" in cited_phase_raw.lower():
            cited_phase = CitedPhase.APPEAL

        category_raw = citation.findtext("category", default="")
        categories = _parse_citation_category(category_raw)

        # Patent citation
        patcit_elem = citation.find("patcit")
        if patcit_elem is not None:
            doc_id = patcit_elem.find("document-id")
            pat_citation = PatentCitation(
                publication_number=_text(doc_id, "doc-number"),
                priority_date=_text(doc_id, "date") or _text(doc_id, "priority-date"),
                publication_date=_text(doc_id, "date"),
                assignee=_text(doc_id, "document-author") or _text(doc_id, "applicant-name"),
                title=_text(doc_id, "title"),
                examiner_cited=cited_by == CitedBy.EXAMINER,
                third_party_cited=cited_by == CitedBy.THIRD_PARTY,
                citation_categories=categories,
                cited_by=cited_by,
                cited_phase=cited_phase,
                patent_publication=patent_number,
            )
            bundle.patcit.append(pat_citation)

        # NPL citation
        nplcit_elem = citation.find("nplcit")
        if nplcit_elem is not None:
            raw_text = _text(nplcit_elem, "text") or _text(nplcit_elem, "nplcit")
            parsed = _parse_npl_citation_text(raw_text)

            # Extract XP number if present
            xp_match = re.search(r'XP\s*(\d+)', raw_text or "", re.IGNORECASE)
            xp_number = f"XP{xp_match.group(1)}" if xp_match else None

            npl_citation = NplCitation(
                xp_number=xp_number,
                title=parsed.get("title"),
                authors=parsed.get("authors", []),
                source_publication=parsed.get("source_publication"),
                publication_date=parsed.get("publication_date"),
                citation_categories=categories,
                cited_by=cited_by,
                cited_phase=cited_phase,
                patent_publication=patent_number,
                raw_citation_text=raw_text,
            )
            bundle.nplcit.append(npl_citation)

    bundle.retrieval_metadata = {
        "patent_number": patent_number,
        "patcit_count": len(bundle.patcit),
        "nplcit_count": len(bundle.nplcit),
    }

    return bundle


def parse_search_xml(xml_content: str | bytes) -> list[dict[str, Any]]:
    """
    Parse EPO OPS search results XML.

    Returns a list of publication references with basic metadata.
    """
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8", errors="replace")

    root = _strip_namespaces(ET.fromstring(xml_content))
    results = []

    for result in _find_all(root, "search-result"):
        doc_id = result.find("publication-reference/document-id")
        if doc_id is None:
            continue

        pub_number = _text(doc_id, "doc-number")
        pub_date = _text(doc_id, "date")
        title_elem = result.find("title")
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else None

        results.append({
            "publication_number": pub_number,
            "publication_date": pub_date,
            "title": title,
        })

    return results