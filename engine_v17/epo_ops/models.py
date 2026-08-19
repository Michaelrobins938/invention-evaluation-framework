"""Data models for EPO OPS citations and NPL evidence records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CitationCategory(str, Enum):
    """EPO citation significance codes."""
    X = "X"           # Particularly relevant document taken alone
    Y = "Y"           # Particularly relevant combined with another document
    A = "A"           # Technological background
    P = "P"           # Intermediate document (published during examination)
    D = "D"           # Document cited in application
    E = "E"           # Earlier patent document
    L = "L"           # Document cited for other reasons
    O = "O"           # Document cited for other reasons (written opinion)
    T = "T"           # Document from patent family
    SAME_FAMILY = "&"  # Document from same patent family (different member)
    PLUS = "+"        # Combination of documents


class CitedBy(str, Enum):
    """Who cited the document."""
    EXAMINER = "examiner"
    APPLICANT = "applicant"
    THIRD_PARTY = "third_party"
    UNKNOWN = "unknown"


class CitedPhase(str, Enum):
    """Phase at which the document was cited."""
    SEARCH = "search"
    EXAMINATION = "examination"
    OPPOSITION = "opposition"
    APPEAL = "appeal"
    UNKNOWN = "unknown"


class MetadataCompleteness(str, Enum):
    """How complete the bibliographic metadata is."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    MINIMAL = "minimal"
    IDENTIFIER_ONLY = "identifier_only"


class EvidenceStatus(str, Enum):
    """Verification status of the evidence record."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    PARTIALLY_VERIFIED = "partially_verified"
    IDENTITY_ENRICHED = "identity_enriched"
    SECONDARY_SOURCE = "secondary_source"


@dataclass
class NplCitation:
    """A single NPL citation extracted from EPO OPS citation data."""
    xp_number: str | None = None
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    source_publication: str | None = None
    publication_date: str | None = None
    citation_categories: list[CitationCategory] = field(default_factory=list)
    cited_by: CitedBy = CitedBy.UNKNOWN
    cited_phase: CitedPhase = CitedPhase.UNKNOWN
    patent_publication: str | None = None
    raw_citation_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "xp_number": self.xp_number,
            "title": self.title,
            "authors": self.authors,
            "source_publication": self.source_publication,
            "publication_date": self.publication_date,
            "citation_categories": [c.value for c in self.citation_categories],
            "cited_by": self.cited_by.value,
            "cited_phase": self.cited_phase.value,
            "patent_publication": self.patent_publication,
            "raw_citation_text": self.raw_citation_text,
        }


@dataclass
class NplEvidenceRecord:
    """
    A normalized NPL evidence record.

    This is the canonical internal representation of an NPL citation
    retrieved through the EPO OPS pipeline. It preserves provenance
    and explicitly tracks metadata completeness so the LLM cannot
    fabricate missing bibliographic details.
    """
    source: str = "epo_ops"
    citation_type: str = "npl"
    xp_number: str | None = None
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    source_publication: str | None = None
    publication_date: str | None = None
    citation_categories: list[CitationCategory] = field(default_factory=list)
    cited_by: CitedBy = CitedBy.UNKNOWN
    cited_phase: CitedPhase = CitedPhase.UNKNOWN
    patent_publication: str | None = None
    evidence_status: EvidenceStatus = EvidenceStatus.UNVERIFIED
    metadata_completeness: MetadataCompleteness = MetadataCompleteness.IDENTIFIER_ONLY
    raw_source: str = "epo_ops"
    raw_citation_text: str | None = None
    enrichment_sources: list[str] = field(default_factory=list)
    retrieval_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "citation_type": self.citation_type,
            "xp_number": self.xp_number,
            "title": self.title,
            "authors": self.authors,
            "source_publication": self.source_publication,
            "publication_date": self.publication_date,
            "citation_categories": [c.value for c in self.citation_categories],
            "cited_by": self.cited_by.value,
            "cited_phase": self.cited_phase.value,
            "patent_publication": self.patent_publication,
            "evidence_status": self.evidence_status.value,
            "metadata_completeness": self.metadata_completeness.value,
            "raw_source": self.raw_source,
            "raw_citation_text": self.raw_citation_text,
            "enrichment_sources": self.enrichment_sources,
            "retrieval_notes": self.retrieval_notes,
        }

    @classmethod
    def from_npl_citation(
        cls,
        citation: NplCitation,
        *,
        evidence_status: EvidenceStatus = EvidenceStatus.VERIFIED,
        metadata_completeness: MetadataCompleteness = MetadataCompleteness.PARTIAL,
        retrieval_notes: list[str] | None = None,
    ) -> NplEvidenceRecord:
        """Create an NplEvidenceRecord from a parsed NplCitation."""
        # Determine completeness based on what fields are populated
        fields = [
            citation.title,
            citation.authors,
            citation.source_publication,
            citation.publication_date,
        ]
        populated = sum(1 for f in fields if f)

        if populated == 4:
            mc = MetadataCompleteness.COMPLETE
        elif populated >= 2:
            mc = MetadataCompleteness.PARTIAL
        elif citation.xp_number:
            mc = MetadataCompleteness.IDENTIFIER_ONLY
        else:
            mc = MetadataCompleteness.MINIMAL

        return cls(
            xp_number=citation.xp_number,
            title=citation.title,
            authors=list(citation.authors),
            source_publication=citation.source_publication,
            publication_date=citation.publication_date,
            citation_categories=citation.citation_categories,
            cited_by=citation.cited_by,
            cited_phase=citation.cited_phase,
            patent_publication=citation.patent_publication,
            evidence_status=evidence_status,
            metadata_completeness=mc,
            raw_citation_text=citation.raw_citation_text,
            retrieval_notes=retrieval_notes or [],
        )


@dataclass
class PatentCitation:
    """A single patent citation (patcit) from EPO OPS."""
    publication_number: str | None = None
    priority_date: str | None = None
    publication_date: str | None = None
    assignee: str | None = None
    title: str | None = None
    examiner_cited: bool = False
    third_party_cited: bool = False
    citation_categories: list[CitationCategory] = field(default_factory=list)
    cited_by: CitedBy = CitedBy.UNKNOWN
    cited_phase: CitedPhase = CitedPhase.UNKNOWN
    patent_publication: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_number": self.publication_number,
            "priority_date": self.priority_date,
            "publication_date": self.publication_date,
            "assignee": self.assignee,
            "title": self.title,
            "examiner_cited": self.examiner_cited,
            "third_party_cited": self.third_party_cited,
            "citation_categories": [c.value for c in self.citation_categories],
            "cited_by": self.cited_by.value,
            "cited_phase": self.cited_phase.value,
            "patent_publication": self.patent_publication,
        }


@dataclass
class CitationBundle:
    """All citations retrieved for a single patent publication."""
    patent_number: str
    patcit: list[PatentCitation] = field(default_factory=list)
    nplcit: list[NplCitation] = field(default_factory=list)
    retrieval_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "patent_number": self.patent_number,
            "patcit": [c.to_dict() for c in self.patcit],
            "nplcit": [c.to_dict() for c in self.nplcit],
            "retrieval_metadata": {
                **self.retrieval_metadata,
                "patcit_count": len(self.patcit),
                "nplcit_count": len(self.nplcit),
            },
        }