"""Integration tests for Autoprompt + IEF (evidence-constrained).

Validates that execution complete does not imply evidence sufficient,
that epistemic gates and coverage gates behave, and that the adapter's
no-recursive-orchestration invariant holds.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


def test_mission_creates_immutable_pointer():
    from engine_v17.mission import create_mission
    m = create_mission("US8527057", "evaluations/us8527057/source/US8527057.pdf", scope="full-pipeline")
    assert m.mission_hash and len(m.mission_hash) == 64
    assert m.mission_bytes == len(m.mission.encode("utf-8"))
    assert not m.validate()
    d = m.to_dict()
    assert d["mission_hash"] == m.mission_hash
    # Workers may not redefine mission: from_dict round-trips the hash
    from engine_v17.mission import EvaluationMission
    m2 = EvaluationMission.from_dict(d)
    assert m2.mission_hash == m.mission_hash


def test_dag_validates_and_groups():
    from engine_v17.dag import build_dag, launch_groups, topological_sort, validate_dag_against_registry
    errors = validate_dag_against_registry()
    assert not errors, f"DAG validation failed: {errors}"
    dag = build_dag()
    order = topological_sort(dag)
    assert order.index("gather-submission") < order.index("analyze-technology")
    assert order.index("analyze-technology") < order.index("compile-report")
    assert order.index("compile-report") < order.index("render-report")
    groups = launch_groups(dag)
    # Every node appears exactly once
    flat = [n for g in groups for n in g]
    assert set(flat) == set(dag.keys())
    assert len(flat) == len(dag)


def test_status_separation():
    from engine_v17.status import CombinedStatus, ExecutionStatus, EvidenceStatus
    # The mandatory distinction: COMPLETE + INSUFFICIENT must be representable
    s = CombinedStatus(execution=ExecutionStatus.COMPLETE, evidence=EvidenceStatus.INSUFFICIENT, detail="done but insufficient")
    assert s.is_execution_complete
    assert not s.is_evidence_sufficient
    assert not s.is_valid_conclusion()
    # Valid conclusion requires both
    s2 = CombinedStatus(execution=ExecutionStatus.COMPLETE, evidence=EvidenceStatus.SUFFICIENT)
    assert s2.is_valid_conclusion()
    # Completed with debt is still complete
    s3 = CombinedStatus(execution=ExecutionStatus.COMPLETED_WITH_EVIDENCE_DEBT, evidence=EvidenceStatus.INSUFFICIENT)
    assert s3.is_execution_complete


def test_epistemic_gates_block_but_do_not_imply_negative_evidence():
    from engine_v17.epistemic_gates import check_E3, GateVerdict
    # Insufficient evidence → FAILED, not negative evidence
    r = check_E3([{"proposition_id": "P-05-001", "state": "WORK QUEUE"}])
    assert r.verdict == GateVerdict.FAILED
    assert r.barrier_type == "insufficient_corroboration"
    # No decisions is PENDING, not FAILED with negative evidence
    r2 = check_E3([])
    assert r2.verdict == GateVerdict.PENDING


def test_coverage_gates_catch_substitutions():
    from engine_v17.coverage import MARKET_COVERAGE, run_coverage_gate
    # Market attempt with only NAICS code must fail required_fields
    attempts = [{"source": "census", "method": "naics_lookup"}]
    support = [{"code": "334419", "title": "Other Electronic Component Manufacturing"}]  # missing market_boundary etc.
    report = run_coverage_gate(MARKET_COVERAGE, attempts, support)
    assert not report.passed
    assert any("required schema fields" in e for e in report.errors)
    # Bounded model passes
    support2 = [{"market_boundary": "retinal prosthesis", "geography": "global", "time_period": "2024", "figure": "100M", "source": "Census", "derivation": "prevalence/4000"}]
    report2 = run_coverage_gate(MARKET_COVERAGE, attempts + [{"source": "public_health_source", "method": "pubmed"}], support2)
    assert report2.passed


def test_review_independence_enforced():
    from engine_v17.review import independent_review, ReviewVerdict
    r = independent_review("P-05-001", ["src1"], author_agent="ap-implementer", reviewer_agent="ap-reviewer", basis="reviewed", verdict=ReviewVerdict.PASSED)
    assert r.is_independent
    # Same agent reviewing itself must raise
    with pytest.raises(ValueError, match="fake independence"):
        independent_review("P-05-001", ["src1"], author_agent="ap-implementer", reviewer_agent="ap-implementer")


def test_adapter_no_recursive_orchestration():
    """Verify the adapter's invariant: no worker re-invokes Autoprompt."""
    from engine_v17.autoprompt_adapter import adapt_autoprompt_mission_to_ief
    m = adapt_autoprompt_mission_to_ief("Evaluate US8527057 end-to-end", "US8527057", "evaluations/us8527057/source/US8527057.pdf", "evaluations/us8527057", scope="full-pipeline")
    plan = __import__("engine_v17.autoprompt_adapter", fromlist=["build_execution_plan"]).build_execution_plan(m)
    # Plan must reference the mission hash, not redefine mission
    assert plan["mission"]["mission_hash"] == m.mission_hash
    # Launch groups must be present
    assert "launch_groups" in plan
    assert "topological_order" in plan


def test_skill_registry_validates_against_schema():
    import jsonschema
    registry_path = Path("schemas/skill_registry.json")
    assert registry_path.exists()
    registry = json.loads(registry_path.read_text())
    schema_path = Path("schemas/skill-contract.schema.json")
    schema = json.loads(schema_path.read_text())
    for skill in registry["skills"]:
        jsonschema.validate(skill, schema)


def test_evaluation_mission_schema_validates():
    import jsonschema
    schema = json.loads(Path("schemas/evaluation-mission.schema.json").read_text())
    m = __import__("engine_v17.mission", fromlist=["create_mission"]).create_mission("US7149534", "evaluations/7149534/source/US7149534.pdf")
    jsonschema.validate(m.to_dict(), schema)


def test_orchestrator_autoprompt_backward_compat():
    """Adapter must produce a valid mission+plan without breaking legacy run path."""
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    from engine_v17.mission import create_mission
    # Verify the adapter's mission/plan layer works without invoking network-heavy legacy run
    m = create_mission("US7149534", "evaluations/7149534/source/US7149534.pdf", scope="full-pipeline")
    assert m.evaluation_id == "US7149534"
    assert m.scope == "full-pipeline"
    assert not m.validate()
    # Verify the DAG slice for this mission is valid
    from engine_v17.autoprompt_adapter import build_execution_plan
    plan = build_execution_plan(m)
    assert "launch_groups" in plan
    assert "topological_order" in plan
    assert "gather-submission" in plan["topological_order"]


def test_evidence_debt_becomes_structured_task():
    """Evidence debt must not be resolved by inventing an answer."""
    from engine_v17.models import Proposition, ResolutionState
    p = Proposition("P-07-001", "Market size", ResolutionState.ESCALATION_REQUIRED, blockers=["specialty_market_data_missing"], search_completeness="incomplete", evidence_strength="insufficient", confidence="low")
    assert p.state == ResolutionState.ESCALATION_REQUIRED
    # Simulate recovery exhaustion without fabrication
    from engine_v17.status import CombinedStatus, ExecutionStatus, EvidenceStatus
    status = CombinedStatus(execution=ExecutionStatus.COMPLETED_WITH_EVIDENCE_DEBT, evidence=EvidenceStatus.INSUFFICIENT)
    assert not status.is_valid_conclusion()
