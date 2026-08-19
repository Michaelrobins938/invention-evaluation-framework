from engine_v17.evidence_gate import (
    EvidenceDecision,
    SourceObject,
    apply_evidence_sufficiency_gate,
    validate_schema,
)


def test_result_retrieval_without_mapping_remains_work_queue():
    source = SourceObject(
        source_identity="US1234567A",
        source_type="patent",
        locator="https://example.test/patent/US1234567A",
        execution_id="EX-03-00001",
        raw_artifact="raw-patent.html",
    )
    decision = apply_evidence_sufficiency_gate(
        proposition_id="P-05-001",
        schema_id="prior_art_disclosure",
        source=source,
        proposition_support=None,
        temporal_relevance=False,
    )
    assert decision.state == EvidenceDecision.WORK_QUEUE
    assert "direct_proposition_support" in decision.errors


def test_complete_prior_art_mapping_can_pass_gate():
    source = SourceObject(
        source_identity="US1234567A",
        source_type="patent",
        locator="https://example.test/patent/US1234567A",
        execution_id="EX-03-00001",
        raw_artifact="raw-patent.html",
    )
    support = {
        "patent_or_publication_id": "US1234567A",
        "jurisdiction": "US",
        "date": "1960-01-01",
        "relevant_passage": "claim passage",
        "claim_element_mapping": {"L1": "yes", "L2": "yes"},
    }
    decision = apply_evidence_sufficiency_gate(
        proposition_id="P-05-001",
        schema_id="prior_art_disclosure",
        source=source,
        proposition_support=support,
        temporal_relevance=True,
    )
    assert decision.state == EvidenceDecision.CONFIRMED_PRESENT
    assert decision.errors == []


def test_schema_validation_reports_exact_missing_fields():
    errors = validate_schema("commercial_adoption", {"source": "product page"})
    assert "product_identity_link" in errors
    assert "date" in errors
