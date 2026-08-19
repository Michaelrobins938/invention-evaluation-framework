"""Coverage gate tests.

The v1.7 framework accepted substitutions where something stronger was
required, and treated them as if the required evidence had been gathered:

  * a single source where >= 2 were required
  * Crossref where a domain-specific source was required
  * a NAICS code where a bounded market model was required
  * a candidate list where a partner-fit analysis was required
  * six references mapped where the complete cited set was required
  * a skipped domain-orientation stage

These gates make each of those machine-enforceable.
"""

from engine_v17.coverage import (
    ALL_GATES,
    CoverageGate,
    SourceRequirement,
    gate_by_name,
    run_all_coverage_gates,
    run_coverage_gate,
)
from engine_v17.execution import ExecutionLedger


def test_patent_gate_requires_two_independent_databases():
    gate = gate_by_name("patent_coverage")
    # Only one database used → fails.
    errors = run_coverage_gate(gate, [
        {"source": "google_patents", "method": "keyword"},
    ]).errors
    assert any("espacenet" in e and "not used" in e for e in errors), errors
    assert any("1 attempts < required 2" in e for e in errors), errors

    # Both databases used → passes.
    assert run_coverage_gate(gate, [
        {"source": "google_patents", "method": "keyword"},
        {"source": "espacenet", "method": "classification"},
    ]).errors == []


def test_patent_gate_accepts_alias_identity():
    gate = gate_by_name("patent_coverage")
    assert run_coverage_gate(gate, [
        {"source": "primary_patent_database", "method": "keyword"},
        {"source": "secondary_patent_database", "method": "prosecution_history"},
    ]).errors == []


def test_literature_gate_rejects_crossref_alone():
    """Crossref is a locator, not a domain source."""
    gate = gate_by_name("literature_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "crossref", "method": "doi_lookup"},
    ]).errors
    assert any("scholarly_database" in e for e in errors), errors
    assert any("technical_database" in e for e in errors), errors


def test_literature_gate_accepts_scholarly_and_technical():
    gate = gate_by_name("literature_coverage")
    assert run_coverage_gate(gate, [
        {"source": "crossref", "method": "doi_lookup"},
        {"source": "pubmed", "method": "keyword"},
        {"source": "engineering_database", "method": "citation_traversal"},
    ]).errors == []


def test_market_gate_rejects_naics_substitution():
    """A NAICS code is not a bounded market model."""
    gate = gate_by_name("market_coverage")
    # Both required sources are present, but the bounded-model schema fields
    # are absent from every support object — that is the substitution defect.
    errors = run_coverage_gate(gate, [
        {"source": "pubmed", "method": "keyword"},
        {"source": "census", "method": "naics_lookup"},
    ], support=[{"naics": "332216"}]).errors
    assert not any("required source" in e for e in errors), errors
    assert any("market_boundary" in e for e in errors), errors
    assert any("derivation" in e for e in errors), errors


def test_market_gate_requires_required_fields():
    gate = gate_by_name("market_coverage")
    # Both sources present but the bounded-model fields are absent.
    errors = run_coverage_gate(gate, [
        {"source": "pubmed", "method": "keyword"},
        {"source": "census", "method": "naics_lookup"},
    ], support=[{"naics": "332216"}]).errors
    assert any("market_boundary" in e for e in errors), errors
    assert any("derivation" in e for e in errors), errors


def test_market_gate_passes_with_bounded_model():
    gate = gate_by_name("market_coverage")
    support = [{
        "market_boundary": "retinal prosthesis",
        "geography": "US",
        "time_period": "2020-2024",
        "figure": 12.0,
        "source": "FDA HDE",
        "derivation": "reference population / 4000",
    }]
    assert run_coverage_gate(gate, [
        {"source": "pubmed", "method": "keyword"},
        {"source": "census", "method": "industry_lookup"},
    ], support=support).errors == []


def test_partner_gate_rejects_candidate_list_substitution():
    """Both sources are used, but the support object is a bare candidate
    list — the required partner-fit schema fields are absent."""
    gate = gate_by_name("partner_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "patent_assignment", "method": "ownership_review"},
        {"source": "company_database", "method": "name_search"},
    ], support=[{"organization": "Acme"}]).errors
    assert not any("required source" in e for e in errors), errors
    assert any("invention_mapping" in e for e in errors), errors
    assert any("sells" in e for e in errors), errors


def test_partner_gate_rejects_when_assignment_source_missing():
    gate = gate_by_name("partner_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "company_database", "method": "name_search"},
    ], support=[{
        "organization": "Acme", "sells": "x", "buys": "y",
        "technical_need": "z", "invention_mapping": "w",
    }]).errors
    assert any("assignment_source" in e for e in errors), errors


def test_partner_gate_accepts_fit_analysis():
    gate = gate_by_name("partner_coverage")
    support = [{
        "organization": "Acme",
        "sells": "AC motors",
        "buys": "phase control",
        "technical_need": "improved phase control",
        "invention_mapping": "shield improvement integrates into line",
    }]
    assert run_coverage_gate(gate, [
        {"source": "patent_assignment", "method": "ownership_review"},
        {"source": "company_database", "method": "capability_review"},
    ], support=support).errors == []


def test_technology_gate_requires_orientation_stage():
    gate = gate_by_name("technology_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "patent_specification", "method": "feature_extraction"},
    ], support=[{"feature_to_benefit": "x → y"}]).errors
    assert any("domain_orientation" in e for e in errors), errors


def test_technology_gate_passes_with_orientation():
    gate = gate_by_name("technology_coverage")
    support = [{
        "feature_to_benefit": "shield → phase control",
        "domain_orientation": "material-dynamics",
    }]
    assert run_coverage_gate(gate, [
        {"source": "patent_specification", "method": "feature_extraction"},
    ], support=support).errors == []


def test_novelty_gate_requires_claim_mapping_field():
    """The gate checks that the claim-element mapping *field* is present; its
    completeness is a downstream semantic judgment. A support object with no
    mapping at all fails the gate."""
    gate = gate_by_name("novelty_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "google_patents", "method": "keyword"},
        {"source": "espacenet", "method": "citation_traversal"},
    ], support=[{"patent_or_publication_id": "US1234567A"}]).errors
    assert any("claim_element_mapping" in e for e in errors), errors


def test_novelty_gate_passes_when_mapping_field_present():
    gate = gate_by_name("novelty_coverage")
    support = [{"claim_element_mapping": {"L1": "yes", "L2": "yes", "L3": "no"}}]
    assert run_coverage_gate(gate, [
        {"source": "google_patents", "method": "keyword"},
        {"source": "espacenet", "method": "citation_traversal"},
    ], support=support).errors == []


def test_all_gates_declared_and_named():
    names = {g.name for g in ALL_GATES}
    for required in {
        "patent_coverage", "literature_coverage", "market_coverage",
        "partner_coverage", "novelty_coverage", "technology_coverage",
    }:
        assert required in names, required


def test_unknown_gate_name_raises():
    import pytest
    with pytest.raises(KeyError):
        gate_by_name("not_a_real_gate")


def test_venue_with_no_attempts_fails_every_gate():
    reports = run_all_coverage_gates({})
    assert len(reports) == len(ALL_GATES)
    assert all(not r.passed for r in reports)


def test_gate_errors_flatten_into_blocker_messages():
    reports = run_all_coverage_gates({})
    messages = [e for r in reports for e in r.errors]
    assert messages, "expected coverage errors for an empty venue"
    assert all(isinstance(m, str) for m in messages)


def test_ledger_attempts_feed_coverage_gates():
    """The execution ledger must expose per-phase attempts so the coverage
    gates can check what was actually gathered rather than what was
    claimed."""
    ledger = ExecutionLedger(run_id="RUN-COV")
    ledger.record("03", "keyword", "google_patents", "retinal electrode")
    ledger.record("03", "classification", "espacenet", "A61N 1/00")
    attempts = ledger.attempts_by_phase("03")
    assert {a["source"] for a in attempts} == {"google_patents", "espacenet"}
    assert all(a["execution_id"] for a in attempts)
    # Ingested artifacts must NOT count as attempts.
    ledger.ingest_artifact("03", "/tmp/novelty.md")
    assert len(ledger.attempts_by_phase("03")) == 2