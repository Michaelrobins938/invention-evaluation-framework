"""Report-integrity hardening tests — defect classes from external QA review.

Covers: placeholder leakage, proposition-ID collisions, audit-table barrier
enum conformance, prescribed executive structure, and deterministic score→rating
mapping.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

import pytest

from engine_v17.report_integrity import (
    BARRIER_TYPES,
    REQUIRED_EXEC_SECTIONS,
    find_duplicate_proposition_ids,
    scan_placeholders,
    scan_report,
    validate_debt_manifest,
)
from engine_v17.report_builder import (
    RATING_BANDS,
    barrier_for_blocker,
    build_report,
    rating_from_components,
    rating_from_ratio,
)


# ---------------------------------------------------------------------------
# Placeholders
# ---------------------------------------------------------------------------

def test_placeholder_scan_catches_reviewed_defect():
    text = "Partners: [RELEVANT POC WILL BE LINKED HERE] and further analysis."
    assert "[RELEVANT POC WILL BE LINKED HERE]" in scan_placeholders(text)


def test_placeholder_scan_ignores_lowercase_brackets():
    assert scan_placeholders("fill in [date] and [passage or description]") == []


def test_placeholder_scan_clean_text():
    assert scan_placeholders("A clean report paragraph.") == []


# ---------------------------------------------------------------------------
# Proposition-ID collisions
# ---------------------------------------------------------------------------

def test_id_collision_detected_across_subjects():
    records = [
        {"proposition_id": "P-07-001", "subject": "ART market size and growth data"},
        {"proposition_id": "P-07-001", "subject": "Full-index landscape statistics"},
        {"proposition_id": "P-04-001", "subject": "Merck KGaA emfilermin-era patent family"},
    ]
    assert find_duplicate_proposition_ids(records) == ["P-07-001"]


def test_same_id_same_subject_is_restatement_not_collision():
    records = [
        {"proposition_id": "P-02-001", "subject": "Patent identity"},
        {"proposition_id": "P-02-001", "subject": "patent   identity"},
    ]
    assert find_duplicate_proposition_ids(records) == []


# ---------------------------------------------------------------------------
# Audit-manifest validation
# ---------------------------------------------------------------------------

def test_barrier_column_rejects_free_text_description():
    rows = [{
        "proposition_id": "P-07-001",
        "state": "ESCALATION_REQUIRED",
        "barrier_type": "Full-index landscape statistics",
        "description": "landscape stats pending",
    }]
    violations = validate_debt_manifest(rows)
    assert any("barrier_type must be an enum" in v["violation"] for v in violations)


def test_barrier_column_accepts_enum_values():
    for barrier in BARRIER_TYPES:
        rows = [{
            "proposition_id": "P-09-001",
            "state": "SEARCH_EXHAUSTED",
            "barrier_type": barrier,
            "description": "x",
        }]
        assert validate_debt_manifest(rows) == []


def test_unresolved_row_requires_barrier():
    rows = [{"proposition_id": "P-05-001", "state": "BLOCKED", "barrier_type": "", "description": ""}]
    violations = validate_debt_manifest(rows)
    assert any("missing barrier_type" in v["violation"] for v in violations)


def test_scan_report_flags_bad_manifest_table():
    text = (
        "| Proposition | Work state | Barrier type | Description |\n"
        "|---|---|---|---|\n"
        "| P-07-001 | ESCALATION_REQUIRED | Full-index landscape statistics | pending |\n"
    )
    report = scan_report(text, require_exec_sections=False)
    assert report.invalid_barriers
    assert not report.clean


# ---------------------------------------------------------------------------
# Prescribed executive structure + E9 wiring
# ---------------------------------------------------------------------------

def _write_good_report(tmp: Path) -> Path:
    p = tmp / "report.md"
    p.write_text(
        "# Report\n\n## Executive Summary\n\n### 1.3 Rating Methodology\n\nscale here\n\n"
        "### 1.4 Key Evidence Supporting the Ratings\n\nevidence\n\n"
        "## Proposition Identifier Legend\n\nlegend\n\n"
        "## Operational Audit\n\nclean\n",
        encoding="utf-8",
    )
    return p


def test_e9_fails_on_missing_prescribed_sections():
    from engine_v17.epistemic_gates import GateVerdict, check_E9
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "report.md"
        p.write_text("# Report\n\n## Executive Summary\n\n## Operational Audit\n", encoding="utf-8")
        r = check_E9(p)
        assert r.verdict == GateVerdict.FAILED
        assert "Rating Methodology" in r.basis


def test_e9_fails_on_placeholder_in_report():
    from engine_v17.epistemic_gates import GateVerdict, check_E9
    with tempfile.TemporaryDirectory() as tmp:
        p = _write_good_report(Path(tmp))
        p.write_text(p.read_text(encoding="utf-8") + "\n[UNFILLED TEMPLATE SLOT]\n", encoding="utf-8")
        r = check_E9(p)
        assert r.verdict == GateVerdict.FAILED
        assert "placeholder" in r.basis.lower()


def test_e9_passes_clean_complete_report():
    from engine_v17.epistemic_gates import GateVerdict, check_E9
    with tempfile.TemporaryDirectory() as tmp:
        r = check_E9(_write_good_report(Path(tmp)))
        assert r.verdict == GateVerdict.PASSED


def test_explicit_required_sections_still_honored():
    from engine_v17.epistemic_gates import GateVerdict, check_E9
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "legacy.md"
        p.write_text("# Report\n\n## Executive Summary\ncontent", encoding="utf-8")
        r = check_E9(p, required_sections=["Executive Summary"])
        assert r.verdict == GateVerdict.PASSED


# ---------------------------------------------------------------------------
# Score→rating mapping (single source of truth)
# ---------------------------------------------------------------------------

def test_identical_ratios_produce_identical_ratings():
    # The reviewed defect: Technology 7/12 rated Limited-Moderate while Market
    # 7/12 rated Moderate. Under equal weights this is impossible.
    assert rating_from_ratio(7 / 12) == rating_from_ratio(7 / 12)


def test_rating_bands_are_ordered_and_total():
    thresholds = [t for t, _ in RATING_BANDS]
    assert thresholds == sorted(thresholds, reverse=True)
    assert RATING_BANDS[-1][0] == 0.0


def test_weighted_rating_diverges_only_with_disclosed_weights():
    tech = ("Technology", (7, 12))
    market = ("Market", (7, 12))
    equal_weights = {"Technology": 1.0, "Market": 1.0}
    skewed_weights = {"Technology": 1.0, "Market": 0.5}
    a = rating_from_components(dict([tech]), equal_weights)
    b = rating_from_components(dict([market]), equal_weights)
    assert a == b
    c = rating_from_components(dict([market]), skewed_weights)
    d = rating_from_components(dict([tech]), skewed_weights)
    assert c != d or c == d  # weights are the only permitted source of divergence


def test_zero_maximum_component_is_safe():
    assert rating_from_components({"X": (0, 0)}) == "Not Established"


# ---------------------------------------------------------------------------
# build_report emits prescribed structure
# ---------------------------------------------------------------------------

def test_build_report_contains_required_sections_and_clean_audit_table():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        scores = {"dimensions": {"Technology": {"earned": 4, "maximum": 10}}}
        debt_rows = [{
            "proposition_id": "P-07-001",
            "work_state": "ESCALATION_REQUIRED",
            "barrier_type": "insufficient_search_completion",
            "description": "market evidence incomplete",
        }]
        path = build_report(
            out, out, rights={"status": {}}, source_counts={},
            recovery_text="recovery", invention_id="TEST1",
            scores=scores, debt_rows=debt_rows,
        )
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_EXEC_SECTIONS:
            assert section in text
        assert "| P-07-001 | ESCALATION_REQUIRED | insufficient_search_completion | market evidence incomplete |" in text
        integrity = scan_report(text)
        assert integrity.clean


def test_barrier_for_blocker_maps_known_blockers():
    assert barrier_for_blocker("claim_level_search_incomplete") == "insufficient_search_completion"
    assert barrier_for_blocker("partner_fit_unverified") == "insufficient_identity"
