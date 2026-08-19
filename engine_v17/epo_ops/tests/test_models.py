"""Tests for EPO OPS models."""

from __future__ import annotations

import pytest

from engine_v17.epo_ops.models import (
    CitationBundle,
    CitationCategory,
    CitedBy,
    CitedPhase,
    EvidenceStatus,
    MetadataCompleteness,
    NplCitation,
    NplEvidenceRecord,
    PatentCitation,
)


class TestCitationCategory:
    def test_standard_categories(self):
        assert CitationCategory.X.value == "X"
        assert CitationCategory.Y.value == "Y"
        assert CitationCategory.A.value == "A"
        assert CitationCategory.P.value == "P"

    def test_same_family_member(self):
        assert CitationCategory.SAME_FAMILY.value == "&"

    def test_plus_combination(self):
        assert CitationCategory.PLUS.value == "+"


class TestNplCitation:
    def test_to_dict_round_trip(self):
        cit = NplCitation(
            xp_number="XP000123456",
            title="Test Article",
            authors=["Author A", "Author B"],
            source_publication="Nature",
            publication_date="2020-01-01",
            citation_categories=[CitationCategory.X],
            cited_by=CitedBy.EXAMINER,
            cited_phase=CitedPhase.SEARCH,
            patent_publication="US5215088A",
            raw_citation_text="Author A; Author B. Test Article. Nature. 2020.",
        )
        d = cit.to_dict()
        assert d["xp_number"] == "XP000123456"
        assert d["title"] == "Test Article"
        assert d["authors"] == ["Author A", "Author B"]
        assert d["cited_by"] == "examiner"
        assert d["cited_phase"] == "search"
        assert d["citation_categories"] == ["X"]


class TestNplEvidenceRecord:
    def test_from_npl_citation_complete(self):
        cit = NplCitation(
            xp_number="XP000123456",
            title="Test Article",
            authors=["Author A"],
            source_publication="Nature",
            publication_date="2020-01-01",
        )
        record = NplEvidenceRecord.from_npl_citation(cit)
        assert record.metadata_completeness == MetadataCompleteness.COMPLETE
        assert record.evidence_status == EvidenceStatus.VERIFIED

    def test_from_npl_citation_partial(self):
        cit = NplCitation(
            xp_number="XP000123456",
            title="Test Article",
            authors=["Author A"],
            source_publication=None,
            publication_date=None,
        )
        record = NplEvidenceRecord.from_npl_citation(cit)
        assert record.metadata_completeness == MetadataCompleteness.PARTIAL

    def test_from_npl_citation_identifier_only(self):
        cit = NplCitation(
            xp_number="XP000123456",
            title=None,
            authors=[],
            source_publication=None,
            publication_date=None,
        )
        record = NplEvidenceRecord.from_npl_citation(cit)
        assert record.metadata_completeness == MetadataCompleteness.IDENTIFIER_ONLY

    def test_to_dict_contains_completeness(self):
        cit = NplCitation(xp_number="XP000123456")
        record = NplEvidenceRecord.from_npl_citation(cit)
        d = record.to_dict()
        assert "metadata_completeness" in d
        assert d["metadata_completeness"] == "identifier_only"
        assert d["evidence_status"] == "verified"

    def test_enrichment_tracking(self):
        cit = NplCitation(xp_number="XP000123456", title="Test")
        record = NplEvidenceRecord.from_npl_citation(
            cit,
            retrieval_notes=["Retrieved via EPO OPS"],
        )
        record.enrichment_sources.append("crossref")
        d = record.to_dict()
        assert "crossref" in d["enrichment_sources"]
        assert "Retrieved via EPO OPS" in d["retrieval_notes"]


class TestPatentCitation:
    def test_to_dict(self):
        cit = PatentCitation(
            publication_number="US5215088A",
            priority_date="1990-01-01",
            publication_date="1993-04-06",
            assignee="Blackrock Neurotech",
            title="Three-Dimensional Electrode Device",
            examiner_cited=True,
            citation_categories=[CitationCategory.X],
        )
        d = cit.to_dict()
        assert d["publication_number"] == "US5215088A"
        assert d["examiner_cited"] is True
        assert d["citation_categories"] == ["X"]


class TestCitationBundle:
    def test_empty_bundle(self):
        bundle = CitationBundle(patent_number="US5215088A")
        d = bundle.to_dict()
        assert d["patent_number"] == "US5215088A"
        assert d["patcit"] == []
        assert d["nplcit"] == []

    def test_bundle_with_citations(self):
        bundle = CitationBundle(patent_number="US5215088A")
        bundle.patcit.append(
            PatentCitation(publication_number="US1234567A", title="Prior Art")
        )
        bundle.nplcit.append(
            NplCitation(xp_number="XP000123456", title="NPL Article")
        )
        d = bundle.to_dict()
        assert len(d["patcit"]) == 1
        assert len(d["nplcit"]) == 1
        assert d["retrieval_metadata"]["patcit_count"] == 1
        assert d["retrieval_metadata"]["nplcit_count"] == 1