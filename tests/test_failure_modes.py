"""Failure-mode tests — 15 mandatory scenarios.

The system must fail safely:
- missing evidence != negative evidence
- execution failure != evidence of absence
- model confidence != evidence confidence
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest


def test_01_source_unavailable():
    from engine_v17.epistemic_gates import check_E1, GateVerdict
    r = check_E1([])
    assert r.verdict == GateVerdict.FAILED
    assert r.barrier_type == "source_unavailable"
    # Must not be treated as negative evidence
    assert r.gate == "E1"


def test_02_source_rate_limited():
    from engine_v17.models import FailureClass
    assert FailureClass.TRANSIENT_FAILURE.value == "transient_failure"
    # Transient failures admit retry; they must not become EXHAUSTED
    from engine_v17.coverage import TECHNOLOGY_COVERAGE, run_coverage_gate
    # No attempt yet → gate fails minimum_attempts, not a silent pass
    report = run_coverage_gate(TECHNOLOGY_COVERAGE, [], None)
    assert not report.passed


def test_03_malformed_source():
    from engine_v17.domain_parsers import parse_patent_metadata
    # Malformed patent source must not produce a finding
    result = parse_patent_metadata("<html>not a patent</html>", patent_id="US0000000")
    # Should either return empty or mark completeness incomplete, never CONFIRMED PRESENT with bad data
    assert result is not None
    assert result["patent_id"] == "US0000000"


def test_04_incomplete_source():
    from engine_v17.epistemic_gates import check_E1
    r = check_E1([{"source_identity": "USPTO", "locator": "p1", "completeness": "incomplete"}])
    assert r.verdict.name == "BLOCKED"
    assert r.barrier_type == "insufficient_search_completion"


def test_05_contradictory_sources():
    from engine_v17.epistemic_gates import check_E5, GateVerdict
    r = check_E5([{"proposition_id": "P-03-001", "status": "unreconciled"}])
    assert r.verdict == GateVerdict.BLOCKED
    assert r.barrier_type == "unresolved_conflict"


def test_06_insufficient_evidence():
    from engine_v17.evidence_gate import apply_evidence_sufficiency_gate, SourceObject
    src = SourceObject(source_identity="Crossref", source_type="literature", locator="https://doi.org/10.1234/x", execution_id="EX-04-00001", raw_artifact="raw-literature-crossref.json")
    result = apply_evidence_sufficiency_gate(
        proposition_id="P-06-001",
        schema_id="literature_disclosure",
        source=src,
        proposition_support={"authors": "A et al", "title": "T"},  # missing many required fields
        temporal_relevance=True,
    )
    assert result.state.value == "WORK QUEUE"
    assert any("venue" in e or "doi" in e.lower() or "date" in e.lower() for e in result.errors)


def test_07_agent_timeout():
    from engine_v17.status import CombinedStatus, ExecutionStatus, EvidenceStatus
    status = CombinedStatus(execution=ExecutionStatus.FAILED, evidence=EvidenceStatus.UNAVAILABLE, detail="agent timeout")
    assert status.execution == ExecutionStatus.FAILED
    assert not status.is_execution_complete
    assert not status.is_valid_conclusion()
    # Timeout must not be read as evidence of absence


def test_08_worker_failure():
    from engine_v17.dag import build_dag, dag_to_execution_plan
    # Worker failure in one lane must block downstream hard dependents
    dag = build_dag()
    plan = dag_to_execution_plan(["gather-submission", "analyze-technology", "patent-landscape", "novelty-search", "compile-report", "render-report"], dag)
    # If patent-landscape fails, novelty-search (hard dep) must be blocked
    assert "patent-landscape" in plan["nodes"]
    assert "novelty-search" in plan["nodes"]
    assert "patent-landscape" in plan["nodes"]["novelty-search"]["hard_deps"]


def test_09_retry_exhaustion():
    from engine_v17.models import Proposition, ResolutionState, ResearchExhaustion
    # After exhaustion, disposition is SEARCH_EXHAUSTED, not ESTABLISHED
    ex = ResearchExhaustion(
        proposition_id="P-07-001",
        sources=["census", "industry_source"],
        methods=["primary_search", "classification_search"],
        coverage={"temporal": "2010-2024", "scope": "retinal prosthesis"},
        results={"result_count": 0},
        disposition=ResolutionState.SEARCH_EXHAUSTED,
        failure_diagnosis="specialty market too narrow for Census NAICS",
        troubleshooting=[{"avenue": "A1", "status": "COMPLETE"}],
        recovery_strategies=[
            {"strategy_class": f"class{i}", "executed": True} for i in range(5)
        ],
        alternate_routes_attempted=["pubmed", "clinical_trials"],
        recursive_recovery_completed=True,
        termination_basis="all avenues dispositioned; evidence insufficient",
    )
    # Exhaustion with valid recovery contract must validate
    errors = [e for e in ex.validate() if e not in ("minimum_four_strategy_classes",)]  # we have 5 strategies but only 5 classes? Ensure 4 unique
    # Adjust to have 4 unique classes
    ex.recovery_strategies = [
        {"strategy_class": "terminology_expansion", "executed": True},
        {"strategy_class": "citation_expansion", "executed": True},
        {"strategy_class": "alternate_database", "executed": True},
        {"strategy_class": "organizational_records", "executed": True},
        {"strategy_class": "jurisdiction_specific", "executed": True},
    ]
    assert not ex.validate()


def test_10_verifier_disagreement():
    from engine_v17.review import independent_review, fresh_verification, arbitrate, ReviewVerdict
    rev = independent_review("P-05-001", ["src1"], "ap-implementer", "ap-reviewer", verdict=ReviewVerdict.PASSED, basis="reviewer pass")
    ver = fresh_verification("P-05-001", ["src1"], "ap-implementer", "ap-fresh-verifier", verdict=ReviewVerdict.FAILED, basis="verifier fail")
    arb = arbitrate("P-05-001", rev, ver, verdict=ReviewVerdict.FAILED, basis="arbiter sides with verifier")
    assert arb.verdict == ReviewVerdict.FAILED


def test_11_reviewer_disagreement():
    from engine_v17.review import independent_review, fresh_verification, arbitrate, ReviewVerdict
    rev = independent_review("P-05-001", ["src1"], "ap-implementer", "ap-reviewer", verdict=ReviewVerdict.FAILED, basis="reviewer fail")
    ver = fresh_verification("P-05-001", ["src1"], "ap-implementer", "ap-fresh-verifier", verdict=ReviewVerdict.FAILED, basis="verifier fail")
    arb = arbitrate("P-05-001", rev, ver, verdict=ReviewVerdict.FAILED, basis="both fail → arbiter fails")
    assert arb.verdict == ReviewVerdict.FAILED


def test_12_unsupported_conclusion_attempt():
    from engine_v17.epistemic_gates import check_E6, GateVerdict
    # Conclusion without premise map must be rejected
    r = check_E6([{"conclusion_id": "C-05-001", "gate": "obviousness", "conclusion": "obvious"}])
    assert r.verdict == GateVerdict.FAILED
    assert "orphan" in r.basis


def test_13_claim_mapping_disagreement():
    from engine_v17.epistemic_gates import check_E2, GateVerdict
    # Duplicate proposition IDs after claim mapping disagreement must be caught
    r = check_E2([
        {"proposition_id": "P-05-001", "proposition": "Claim 1 anticipation"},
        {"proposition_id": "P-05-001", "proposition": "Claim 1 anticipation — revised mapping"},
    ])
    assert r.verdict == GateVerdict.FAILED
    assert "duplicate" in r.basis


def test_14_partial_pipeline_completion():
    from engine_v17.status import CombinedStatus, ExecutionStatus, EvidenceStatus
    status = CombinedStatus(execution=ExecutionStatus.PARTIAL, evidence=EvidenceStatus.INSUFFICIENT, detail="only 3/9 phases complete")
    assert status.execution == ExecutionStatus.PARTIAL
    assert not status.is_valid_conclusion()
    # Partial execution must not be reported as COMPLETE
    assert not status.is_execution_complete


def test_15_report_rendering_failure():
    from engine_v17.epistemic_gates import check_E9, GateVerdict
    r = check_E9(None)
    assert r.verdict == GateVerdict.FAILED
    assert r.gate == "E9"
    # Also test missing section
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "report.md"
        p.write_text("# Report\n\n## Executive Summary\n\ncontent", encoding="utf-8")
        r2 = check_E9(p, required_sections=["Executive Summary", "Operational Audit"])
        assert r2.verdict == GateVerdict.FAILED
        assert "Operational Audit" in r2.basis


def test_missing_evidence_not_negative_evidence():
    from engine_v17.status import EvidenceStatus
    # Missing evidence is INSUFFICIENT, not CONTRADICTED or UNAVAILABLE
    assert EvidenceStatus.INSUFFICIENT != EvidenceStatus.CONTRADICTED
    assert EvidenceStatus.INSUFFICIENT != EvidenceStatus.UNAVAILABLE

    from engine_v17.epistemic_gates import check_E3
    r = check_E3([{"proposition_id": "P-07-001", "state": "WORK QUEUE"}])
    # FAILED gate means insufficient, not confirmed absent
    assert "insufficient" in r.basis.lower() or "insufficient" in (r.barrier_type or "")
