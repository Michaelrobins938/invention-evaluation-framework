"""IEF Epistemic Gates E0–E9.

Autoprompt execution gates and IEF evidence gates remain separate.
These gates answer: does the resulting evidence actually justify the conclusion?
Execution complete != evaluation valid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class GateVerdict(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    BLOCKED = "BLOCKED"


@dataclass
class GateResult:
    gate: str  # E0..E9
    name: str
    verdict: GateVerdict
    basis: str
    evidence_refs: list[str] = field(default_factory=list)
    barrier_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "name": self.name,
            "verdict": self.verdict.value,
            "basis": self.basis,
            "evidence_refs": self.evidence_refs,
            "barrier_type": self.barrier_type,
        }


# ---------------------------------------------------------------------------
# Gate definitions
# ---------------------------------------------------------------------------

GATE_DEFINITIONS: dict[str, dict[str, str]] = {
    "E0": {"name": "Intake validity", "question": "Can we establish what is being evaluated?"},
    "E1": {"name": "Source integrity", "question": "Are sources valid, readable, correctly identified, and sufficiently complete?"},
    "E2": {"name": "Proposition integrity", "question": "Have material conclusions been decomposed into atomic propositions?"},
    "E3": {"name": "Evidence sufficiency", "question": "Does each proposition have sufficient supporting evidence?"},
    "E4": {"name": "Temporal validity", "question": "Is the evidence valid for the relevant date/time?"},
    "E5": {"name": "Contradiction check", "question": "Is there conflicting evidence that materially changes the conclusion?"},
    "E6": {"name": "Analytical validity", "question": "Does the conclusion actually follow from the evidence?"},
    "E7": {"name": "Independent review", "question": "Can an independent reviewer reproduce/validate the conclusion?"},
    "E8": {"name": "Fresh verification", "question": "Can a fresh verifier independently validate critical findings?"},
    "E9": {"name": "Report integrity", "question": "Does the final report preserve evidence status, uncertainty, and limitations?"},
}


def check_E0(submission_path: Path | None, proposition_count: int = 0) -> GateResult:
    """E0 — Intake validity: can we establish what is being evaluated?"""
    if submission_path is None or not submission_path.exists():
        return GateResult("E0", GATE_DEFINITIONS["E0"]["name"], GateVerdict.FAILED,
                          "submission record missing", barrier_type="source_unavailable")
    if submission_path.stat().st_size == 0:
        return GateResult("E0", GATE_DEFINITIONS["E0"]["name"], GateVerdict.FAILED,
                          "submission record empty", barrier_type="insufficient_identity")
    return GateResult("E0", GATE_DEFINITIONS["E0"]["name"], GateVerdict.PASSED,
                      f"submission present: {submission_path.name}")


def check_E1(sources: list[dict[str, Any]]) -> GateResult:
    """E1 — Source integrity: valid, readable, correctly identified, complete.

    P2 hardening: distinguish external/primary sources from derived worker artifacts.
    Only external sources (patent HTML, Crossref, WorldBank, EPO OPS, Google Patents)
    count as sources. Worker outputs (ap-synthesizer, ap-scribe, ledger, compiled
    report) are evidence interpretations, not sources. E1 must not be inflated by
    counting 6 external artifacts as 9 sources because 3 internal artifacts were added.

    Ontology:
      external / primary source  → SourceObject → Evidence item
      worker output              → interpretation → Proposition
      provenance / ledger        → record, not source
    """
    if not sources:
        return GateResult("E1", GATE_DEFINITIONS["E1"]["name"], GateVerdict.FAILED,
                          "no sources supplied", barrier_type="source_unavailable")
    # Filter to external/primary sources for integrity count; internal artifacts are derived
    external_sources = [s for s in sources if s.get("source_type", "external") in ("external", "primary", "external_source")]
    # If no explicit type, treat as external for backward compat but mark derived types separately
    derived = [s for s in sources if s.get("source_type") in ("derived", "worker_output", "provenance", "ledger")]
    # If caller supplied ontology-clean sources, external_sources is authoritative
    countable = external_sources if external_sources else ([s for s in sources if s.get("source_type") not in ("derived", "worker_output", "provenance", "ledger")] if any("source_type" in s for s in sources) else sources)
    if not countable:
        return GateResult("E1", GATE_DEFINITIONS["E1"]["name"], GateVerdict.FAILED,
                          "no external sources supplied (only derived/provenance artifacts)", barrier_type="source_unavailable")
    missing = [s for s in countable if not s.get("source_identity") or not s.get("locator")]
    if missing:
        return GateResult("E1", GATE_DEFINITIONS["E1"]["name"], GateVerdict.FAILED,
                          f"{len(missing)} external sources missing identity/locator", barrier_type="insufficient_identity")
    incomplete = [s for s in countable if s.get("completeness") == "incomplete"]
    if incomplete:
        return GateResult("E1", GATE_DEFINITIONS["E1"]["name"], GateVerdict.BLOCKED,
                          f"{len(incomplete)} external sources incomplete", barrier_type="insufficient_search_completion")
    basis = f"{len(countable)} external sources verified"
    if derived:
        basis += f" ({len(derived)} derived/provenance artifacts not counted as sources)"
    return GateResult("E1", GATE_DEFINITIONS["E1"]["name"], GateVerdict.PASSED,
                      basis, evidence_refs=[s["source_identity"] for s in countable])


def check_E2(propositions: list[dict[str, Any]]) -> GateResult:
    """E2 — Proposition integrity: atomic decomposition, stable ID+version."""
    if not propositions:
        return GateResult("E2", GATE_DEFINITIONS["E2"]["name"], GateVerdict.FAILED,
                          "no propositions registered", barrier_type="insufficient_identity")
    ids = [p.get("proposition_id", "") for p in propositions]
    if len(ids) != len(set(ids)):
        dups = [x for x in ids if ids.count(x) > 1]
        return GateResult("E2", GATE_DEFINITIONS["E2"]["name"], GateVerdict.FAILED,
                          f"duplicate proposition IDs: {set(dups)}", barrier_type="scope_mismatch")
    non_atomic = [p for p in propositions if len(p.get("proposition", "").split(" and ")) > 3]
    # Heuristic: proposition containing multiple "and" conjunctions likely not atomic
    if non_atomic:
        return GateResult("E2", GATE_DEFINITIONS["E2"]["name"], GateVerdict.PENDING,
                          f"{len(non_atomic)} propositions may not be atomic", barrier_type="scope_mismatch")
    return GateResult("E2", GATE_DEFINITIONS["E2"]["name"], GateVerdict.PASSED,
                      f"{len(propositions)} atomic propositions with stable IDs")


def check_E3(evidence_decisions: list[dict[str, Any]]) -> GateResult:
    """E3 — Evidence sufficiency: each proposition passes Sufficiency Gate."""
    if not evidence_decisions:
        return GateResult("E3", GATE_DEFINITIONS["E3"]["name"], GateVerdict.PENDING,
                          "no evidence decisions yet", barrier_type="insufficient_search_completion")
    insufficient = [d for d in evidence_decisions if d.get("state") != "CONFIRMED PRESENT" and d.get("state") != "CONFIRMED ABSENT"]
    if insufficient:
        return GateResult("E3", GATE_DEFINITIONS["E3"]["name"], GateVerdict.FAILED,
                          f"{len(insufficient)}/{len(evidence_decisions)} propositions insufficient",
                          evidence_refs=[d["proposition_id"] for d in insufficient],
                          barrier_type="insufficient_corroboration")
    return GateResult("E3", GATE_DEFINITIONS["E3"]["name"], GateVerdict.PASSED,
                      f"all {len(evidence_decisions)} propositions sufficient")


def check_E4(evidence_dates: list[dict[str, Any]], critical_date: str | None = None) -> GateResult:
    """E4 — Temporal validity: evidence valid for relevant date/time."""
    if critical_date is None:
        return GateResult("E4", GATE_DEFINITIONS["E4"]["name"], GateVerdict.NOT_APPLICABLE,
                          "no critical date supplied")
    if not evidence_dates:
        return GateResult("E4", GATE_DEFINITIONS["E4"]["name"], GateVerdict.PENDING,
                          "no evidence dates to check", barrier_type="insufficient_search_completion")
    # Check post-critical-date evidence leaking into pre-filing analysis
    post_filing = [e for e in evidence_dates if e.get("evidence_date", "") > critical_date]
    if post_filing:
        return GateResult("E4", GATE_DEFINITIONS["E4"]["name"], GateVerdict.FAILED,
                          f"{len(post_filing)} evidence items post-date critical date {critical_date}",
                          evidence_refs=[e.get("source_identity", "") for e in post_filing],
                          barrier_type="insufficient_temporal_match")
    return GateResult("E4", GATE_DEFINITIONS["E4"]["name"], GateVerdict.PASSED,
                      f"all {len(evidence_dates)} evidence items pre-date critical date")


def check_E5(contradictions: list[dict[str, Any]]) -> GateResult:
    """E5 — Contradiction check: conflicting evidence reconciled."""
    if not contradictions:
        return GateResult("E5", GATE_DEFINITIONS["E5"]["name"], GateVerdict.PASSED,
                          "no contradictions reported")
    unresolved = [c for c in contradictions if c.get("status") != "reconciled"]
    if unresolved:
        return GateResult("E5", GATE_DEFINITIONS["E5"]["name"], GateVerdict.BLOCKED,
                          f"{len(unresolved)} contradictions unresolved",
                          evidence_refs=[c.get("proposition_id", "") for c in unresolved],
                          barrier_type="unresolved_conflict")
    return GateResult("E5", GATE_DEFINITIONS["E5"]["name"], GateVerdict.PASSED,
                      f"{len(contradictions)} contradictions reconciled")


def check_E6(conclusions: list[dict[str, Any]]) -> GateResult:
    """E6 — Analytical validity: conclusion follows from evidence (premise map)."""
    if not conclusions:
        return GateResult("E6", GATE_DEFINITIONS["E6"]["name"], GateVerdict.NOT_APPLICABLE,
                          "no analytical conclusions to check")
    orphan = [c for c in conclusions if not c.get("premises")]
    if orphan:
        return GateResult("E6", GATE_DEFINITIONS["E6"]["name"], GateVerdict.FAILED,
                          f"{len(orphan)} conclusions without premise map (orphan conclusions)",
                          barrier_type="insufficient_identity")
    # Check premises reference only established findings
    bad_premise = [c for c in conclusions if any(p.get("status") in ("EXHAUSTED", "BLOCKED", "REQUIRES_VERIFICATION") for p in c.get("premises", []))]
    if bad_premise:
        return GateResult("E6", GATE_DEFINITIONS["E6"]["name"], GateVerdict.FAILED,
                          f"{len(bad_premise)} conclusions use work-state premises as evidence",
                          barrier_type="insufficient_corroboration")
    return GateResult("E6", GATE_DEFINITIONS["E6"]["name"], GateVerdict.PASSED,
                      f"{len(conclusions)} conclusions with valid premise maps")


def check_E7(reviewer_verdict: dict[str, Any] | None) -> GateResult:
    """E7 — Independent review: independent reviewer reproduces/validates."""
    if reviewer_verdict is None:
        return GateResult("E7", GATE_DEFINITIONS["E7"]["name"], GateVerdict.PENDING,
                          "independent review not yet run", barrier_type="insufficient_search_completion")
    verdict = reviewer_verdict.get("verdict", "")
    if verdict == "BLOCKED":
        return GateResult("E7", GATE_DEFINITIONS["E7"]["name"], GateVerdict.BLOCKED,
                          reviewer_verdict.get("basis", "reviewer blocked"),
                          barrier_type=reviewer_verdict.get("barrier_type", "unresolved_conflict"))
    if verdict == "FAILED":
        return GateResult("E7", GATE_DEFINITIONS["E7"]["name"], GateVerdict.FAILED,
                          reviewer_verdict.get("basis", "reviewer disagreed"),
                          barrier_type="unresolved_conflict")
    if verdict == "PASSED":
        return GateResult("E7", GATE_DEFINITIONS["E7"]["name"], GateVerdict.PASSED,
                          reviewer_verdict.get("basis", "reviewer passed"))
    return GateResult("E7", GATE_DEFINITIONS["E7"]["name"], GateVerdict.PENDING,
                      f"unknown reviewer verdict: {verdict}")


def check_E8(verifier_verdict: dict[str, Any] | None) -> GateResult:
    """E8 — Fresh verification: fresh verifier independently validates."""
    if verifier_verdict is None:
        return GateResult("E8", GATE_DEFINITIONS["E8"]["name"], GateVerdict.PENDING,
                          "fresh verification not yet run", barrier_type="insufficient_search_completion")
    verdict = verifier_verdict.get("verdict", "")
    if verdict == "BLOCKED":
        return GateResult("E8", GATE_DEFINITIONS["E8"]["name"], GateVerdict.BLOCKED,
                          verifier_verdict.get("basis", "verifier blocked"),
                          barrier_type=verifier_verdict.get("barrier_type", "unresolved_conflict"))
    if verdict == "FAILED":
        return GateResult("E8", GATE_DEFINITIONS["E8"]["name"], GateVerdict.FAILED,
                          verifier_verdict.get("basis", "verifier disagreed"),
                          barrier_type="unresolved_conflict")
    if verdict == "PASSED":
        return GateResult("E8", GATE_DEFINITIONS["E8"]["name"], GateVerdict.PASSED,
                          verifier_verdict.get("basis", "fresh verifier passed"))
    return GateResult("E8", GATE_DEFINITIONS["E8"]["name"], GateVerdict.PENDING,
                      f"unknown verifier verdict: {verdict}")


def check_E9(report_path: Path | None, required_sections: list[str] | None = None) -> GateResult:
    """E9 — Report integrity: rendered report preserves evidence status, uncertainty, limitations.

    Beyond section presence, E9 runs deterministic integrity scans
    (report_integrity.scan_report): template-placeholder leakage, audit-manifest
    barrier-type enum conformance. A report failing these scans is a pipeline
    defect and blocks delivery regardless of evidence state.
    """
    if report_path is None or not report_path.exists():
        return GateResult("E9", GATE_DEFINITIONS["E9"]["name"], GateVerdict.FAILED,
                          "report artifact missing", barrier_type="source_unavailable")
    if required_sections is None:
        from .report_integrity import REQUIRED_EXEC_SECTIONS
        required_sections = ["Executive Summary", "Operational Audit", *REQUIRED_EXEC_SECTIONS]
    try:
        content = report_path.read_text(encoding="utf-8")
    except Exception as e:
        return GateResult("E9", GATE_DEFINITIONS["E9"]["name"], GateVerdict.FAILED,
                          f"report unreadable: {e}", barrier_type="source_unavailable")
    missing = [s for s in required_sections if s not in content]
    if missing:
        return GateResult("E9", GATE_DEFINITIONS["E9"]["name"], GateVerdict.FAILED,
                          f"report missing sections: {missing}", barrier_type="insufficient_identity")

    from .report_integrity import scan_report
    integrity = scan_report(content)
    if integrity.placeholders:
        return GateResult("E9", GATE_DEFINITIONS["E9"]["name"], GateVerdict.FAILED,
                          f"template placeholder residue in delivered report: {integrity.placeholders}",
                          barrier_type="insufficient_identity")
    if integrity.invalid_barriers:
        detail = "; ".join(
            f"{v.get('proposition_id') or 'row ' + str(v['row'])}: {v['violation']}"
            for v in integrity.invalid_barriers[:3]
        )
        return GateResult("E9", GATE_DEFINITIONS["E9"]["name"], GateVerdict.FAILED,
                          f"audit-manifest integrity failures: {detail}",
                          barrier_type="scope_mismatch")
    if "PARTIALLY_ESTABLISHED" in content or "CONFIRMED PRESENT" in content or "WORK QUEUE" in content:
        # Legacy evidence states in rendered report would be a leak
        pass
    return GateResult("E9", GATE_DEFINITIONS["E9"]["name"], GateVerdict.PASSED,
                      f"report present ({report_path.name}) with required sections")


def run_all_gates(
    submission_path: Path | None = None,
    sources: list[dict[str, Any]] | None = None,
    propositions: list[dict[str, Any]] | None = None,
    evidence_decisions: list[dict[str, Any]] | None = None,
    evidence_dates: list[dict[str, Any]] | None = None,
    critical_date: str | None = None,
    contradictions: list[dict[str, Any]] | None = None,
    conclusions: list[dict[str, Any]] | None = None,
    reviewer_verdict: dict[str, Any] | None = None,
    verifier_verdict: dict[str, Any] | None = None,
    report_path: Path | None = None,
) -> list[GateResult]:
    """Run all E-gates and return results. Execution gates are not run here."""
    return [
        check_E0(submission_path),
        check_E1(sources or []),
        check_E2(propositions or []),
        check_E3(evidence_decisions or []),
        check_E4(evidence_dates or [], critical_date),
        check_E5(contradictions or []),
        check_E6(conclusions or []),
        check_E7(reviewer_verdict),
        check_E8(verifier_verdict),
        check_E9(report_path),
    ]


def gates_blocking_delivery(results: list[GateResult]) -> list[GateResult]:
    """Return gates that block delivery (FAILED or BLOCKED)."""
    return [r for r in results if r.verdict in (GateVerdict.FAILED, GateVerdict.BLOCKED)]
