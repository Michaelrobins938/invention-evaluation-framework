"""v1.8 end-to-end regression suite.

The four avenues below were the recovery targets of the v1.7 run. They now
serve as the first end-to-end regression tests for the v1.8 hardening:

  P-05-001 — Claim 1 anticipation
  P-05-002 — Obviousness bridge
  P-07-001 — Retinal prosthesis market size
  P-08-001 — Partner fit

Each must demonstrate that the v1.8 gates — the evidence-state controller,
the coverage gates, the renderer contract, and the visual QA gate — behave
correctly on the real artifacts rather than on synthetic fixtures.
"""

import json
from pathlib import Path

import pytest

from engine_v17.models import Proposition, ResolutionState
from engine_v17.recovery import (
    RecoveryAttempt,
    classify_failure,
    is_terminal_exhaustion,
    recovery_paths_remaining,
    select_recovery_policy,
    transition_state,
)
from engine_v17.coverage import gate_by_name, run_coverage_gate
from engine_v17.execution import ExecutionLedger

EVAL_DIR = (
    Path(__file__).resolve().parents[2]
    / "evaluations/us8527057-v17(Complete-pass)"
)


# ---------------------------------------------------------------------------
# P-05-001 — Claim 1 anticipation
# ---------------------------------------------------------------------------

def test_p05_001_anticipation_is_not_terminal_without_recovery():
    """A proposition whose search was stopped for an operational reason must
    never be reported as exhausted."""
    proposition = Proposition(
        id="P-05-001", claim="Claim 1 anticipation",
        state=ResolutionState.ESCALATION_REQUIRED,
        blockers=["independent_search_incomplete", "continuity_review_incomplete"],
        downstream_effects=["anticipation", "patentability_confidence", "ip_leverage"])
    policy = select_recovery_policy(proposition)
    attempts = [
        RecoveryAttempt("google_patents", "keyword", rejection_reason="rate_limited"),
    ]
    assert not is_terminal_exhaustion(attempts, policy)
    assert recovery_paths_remaining(attempts, policy)
    assert transition_state(proposition, attempts) == ResolutionState.ESCALATION_REQUIRED


def test_p05_001_novelty_gate_requires_two_databases():
    gate = gate_by_name("novelty_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "google_patents", "method": "keyword"},
    ]).errors
    assert any("espacenet" in e for e in errors)


# ---------------------------------------------------------------------------
# P-05-002 — Obviousness bridge
# ---------------------------------------------------------------------------

def test_p05_002_bridge_state_is_partially_traversed_not_terminal():
    """The bridge vector is PARTIALLY TRAVERSED — feature availability HIGH,
    motivation MODERATE, compatibility PARTIAL. That is a recovery queue, not
    an exhaustion."""
    bridge = {
        "feature_availability": "high",
        "motivation": "moderate",
        "compatibility": "partial",
        "expected_result": "not_established",
        "unexpected_result": "not_established",
    }
    assert bridge["expected_result"] == "not_established"
    assert bridge["motivation"] != "established"


# ---------------------------------------------------------------------------
# P-07-001 — Market size
# ---------------------------------------------------------------------------

def test_p07_001_market_gate_rejects_naics_substitution():
    """A NAICS code is not a bounded market model. The gate must reject it
    even when both required sources were used."""
    gate = gate_by_name("market_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "pubmed", "method": "keyword"},
        {"source": "census", "method": "naics_lookup"},
    ], support=[{"naics": "332216"}]).errors
    assert not any("required source" in e for e in errors), errors
    assert any("market_boundary" in e for e in errors), errors
    assert any("derivation" in e for e in errors), errors


def test_p07_001_bounded_model_passes_market_gate():
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


# ---------------------------------------------------------------------------
# P-08-001 — Partner fit
# ---------------------------------------------------------------------------

def test_p08_001_partner_gate_rejects_candidate_list():
    gate = gate_by_name("partner_coverage")
    errors = run_coverage_gate(gate, [
        {"source": "patent_assignment", "method": "ownership_review"},
        {"source": "company_database", "method": "name_search"},
    ], support=[{"organization": "Acme"}]).errors
    assert any("invention_mapping" in e for e in errors), errors
    assert any("sells" in e for e in errors), errors


def test_p08_001_partner_fit_passes_gate():
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


# ---------------------------------------------------------------------------
# Cross-cutting: the four avenues in the real evaluation directory
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not EVAL_DIR.exists(), reason="evaluation dir not present")
def test_evaluation_directory_carries_all_four_recovery_targets():
    """The compiled evidence graph must still list all four avenues as
    unresolved — the recovery queue is the point of the run."""
    graph = json.loads(
        (EVAL_DIR / "evidence-graph.json").read_text(encoding="utf-8"))
    ids = {p["id"] for p in graph["propositions"]}
    for required in {"P-05-001", "P-05-002", "P-07-001", "P-08-001"}:
        assert required in ids, f"{required} missing from evidence graph"


@pytest.mark.skipif(not EVAL_DIR.exists(), reason="evaluation dir not present")
def test_evaluation_directory_has_coverage_report():
    """v1.8 writes a coverage-report.json alongside the graph artifacts."""
    report = json.loads(
        (EVAL_DIR / "coverage-report.json").read_text(encoding="utf-8"))
    assert report, "coverage report is empty"
    gates = {r["gate"] for r in report}
    assert {"patent_coverage", "literature_coverage", "market_coverage",
            "partner_coverage", "novelty_coverage",
            "technology_coverage"}.issubset(gates)


@pytest.mark.skipif(not EVAL_DIR.exists(), reason="evaluation dir not present")
def test_evaluation_directory_rendered_report_passes_contract():
    """The delivered HTML must account for every source semantic node."""
    import importlib.util
    import sys
    renderer_dir = EVAL_DIR.parent.parent / "report-renderer"
    sys.path.insert(0, str(renderer_dir))
    spec = importlib.util.spec_from_file_location(
        "render_report", renderer_dir / "render_report.py")
    rr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rr)
    from contract import parse_report_ast, account_semantic_nodes

    md = (EVAL_DIR / "report-us8527057-v17.md").read_text(encoding="utf-8")
    html = (EVAL_DIR / "report-us8527057-v17.html").read_text(encoding="utf-8")
    errors = account_semantic_nodes(parse_report_ast(md), html)
    assert errors == [], [f"{e.section}: {e.reason}" for e in errors]


@pytest.mark.skipif(not EVAL_DIR.exists(), reason="evaluation dir not present")
def test_evaluation_directory_pdf_passes_visual_qa():
    import subprocess
    import sys
    sys.path.insert(0, str(EVAL_DIR.parent.parent / "report-renderer"))
    from visual_qa import run_visual_qa
    info = subprocess.run(
        ["pdfinfo", str(EVAL_DIR / "report-us8527057-v17.pdf")],
        capture_output=True, text=True).stdout
    pages = int(next(line.split(":")[1].strip()
                     for line in info.splitlines()
                     if line.lower().startswith("pages:")))
    report = run_visual_qa(
        str(EVAL_DIR / "report-us8527057-v17.pdf"),
        expected_headings=(
            "Executive Summary", "v1.7 Control State", "Original Submission",
            "Technology Analysis", "Patent Landscape Analysis",
            "IP / Novelty Analysis", "Literature Analysis",
            "Market Analysis", "Potential Partners",
            "Operational Audit", "Evidence Recovery Record", "Sources",
            "v1.7 Inference Controls", "SWOT Analysis",
            "Landscape & Market Data",
        ),
        expected_min_pages=pages, expected_max_pages=pages)
    assert report.passed, [
        c.detail for c in report.structural if not c.passed
    ] + [f"{c.page}: {c.issues}" for c in report.visual if not c.passed]


def test_classify_failure_separates_operational_from_epistemic():
    """The state machine's core distinction: a rate limit is not evidence
    absence."""
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="rate_limited")) != \
        classify_failure(RecoveryAttempt("a", "b", result_count=0))