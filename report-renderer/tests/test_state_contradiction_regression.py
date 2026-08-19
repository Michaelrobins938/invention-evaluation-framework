"""
Forced State-Contradiction Regression Tests
============================================

The v1.8 architectural fix: proposition states are governed by ONE
authoritative Proposition Registry. A downstream artifact (report section,
evidence summary, appendix) that claims a different state is a
state-propagation violation and MUST abort rendering.

These tests inject a forced contradiction — a downstream artifact claiming
ESTABLISHED while the canonical registry says ESCALATION_REQUIRED /
PARTIALLY_ESTABLISHED — and assert that the integrity gate refuses to render.

This is the exact failure mode the user identified in the v1.8 critique:
P-03-003 was simultaneously ESTABLISHED (Evidence Summary) and
ESCALATION_REQUIRED (Appendix C); P-06-005 and P-08-005 had the same
epistemic-state collision.
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contract import (
    PropositionRegistry,
    pre_render_integrity_gate,
    RenderContractFailure,
    RecoveryClass,
    EvidenceDebt,
)

EVAL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "evaluations", "US5215088",
)
LEDGER_PATH = os.path.join(EVAL_DIR, "proposition-ledger.json")
REPORT_PATH = os.path.join(EVAL_DIR, "report.md")


def _load_ledger():
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_report():
    with open(REPORT_PATH, encoding="utf-8") as f:
        return f.read()


def _scores():
    return {
        "invention_id": "US5215088",
        "target_patent": {
            "publication_number": "US5215088A",
            "title": "Three-dimensional electrode device",
            "government_rights": "NSF grant 5-38640-3300",
        },
        "evidence_items": [],
    }


class TestForcedStateContradiction:
    """The canonical registry must reject any downstream state override."""

    def test_p03003_forced_established_aborts(self):
        """P-03-003 forced to ESTABLISHED while registry says ESCALATION_REQUIRED."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        assert reg.state_of("P-03-003") == "ESCALATION_REQUIRED"

        report_md = _load_report().replace(
            "**P-03-003** (Quantitative performance comparison): ESCALATION_REQUIRED",
            "**P-03-003** (Quantitative performance comparison): ESTABLISHED",
        )
        errors = reg.validate_report_consistency(report_md)
        assert len(errors) > 0
        assert any("P-03-003" in str(e) for e in errors)
        assert any("ESCALATION_REQUIRED" in str(e) for e in errors)

    def test_p06005_forced_established_aborts(self):
        """P-06-005 forced to ESTABLISHED while registry says PARTIALLY_ESTABLISHED."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        assert reg.state_of("P-06-005") == "PARTIALLY_ESTABLISHED"

        report_md = _load_report().replace(
            "**P-06-005** (Long-term biocompatibility): PARTIALLY_ESTABLISHED",
            "**P-06-005** (Long-term biocompatibility): ESTABLISHED",
        )
        errors = reg.validate_report_consistency(report_md)
        assert len(errors) > 0
        assert any("P-06-005" in str(e) for e in errors)

    def test_p08005_forced_established_aborts(self):
        """P-08-005 forced to ESTABLISHED while registry says PARTIALLY_ESTABLISHED."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        assert reg.state_of("P-08-005") == "PARTIALLY_ESTABLISHED"

        report_md = _load_report().replace(
            "**P-08-005** (Licensing terms): PARTIALLY_ESTABLISHED",
            "**P-08-005** (Licensing terms): ESTABLISHED",
        )
        errors = reg.validate_report_consistency(report_md)
        assert len(errors) > 0
        assert any("P-08-005" in str(e) for e in errors)

    def test_clean_report_passes_registry(self):
        """The current report.md must be consistent with the registry."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        report_md = _load_report()
        errors = reg.validate_report_consistency(report_md)
        assert errors == [], f"report.md contradicts registry: {errors}"

    def test_pre_render_gate_aborts_on_forced_contradiction(self):
        """The full pre-render gate must abort when a contradiction is injected."""
        ledger = _load_ledger()
        report_md = _load_report().replace(
            "**P-03-003** (Quantitative performance comparison): ESCALATION_REQUIRED",
            "**P-03-003** (Quantitative performance comparison): ESTABLISHED",
        )
        with pytest.raises(RenderContractFailure) as exc_info:
            pre_render_integrity_gate(report_md, _scores(), "", ledger=ledger)
        assert "Proposition Consistency" in str(exc_info.value)
        assert "P-03-003" in str(exc_info.value)

    def test_pre_render_gate_passes_clean_report(self):
        """The full pre-render gate must pass the clean report."""
        ledger = _load_ledger()
        report_md = _load_report()
        # Should not raise
        errors = pre_render_integrity_gate(report_md, _scores(), "", ledger=ledger)
        assert errors == []

    def test_all_propositions_established_boilerplate_aborts(self):
        """'All propositions are now ESTABLISHED' boilerplate must abort."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        report_md = _load_report() + "\n\nAll propositions are now ESTABLISHED.\n"
        errors = reg.validate_report_consistency(report_md)
        assert len(errors) > 0
        assert any("boilerplate" in str(e).lower() or "ESTABLISHED" in str(e) for e in errors)

    def test_unestablished_none_boilerplate_aborts(self):
        """'Unestablished Propositions: NONE' when registry disagrees must abort."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        report_md = _load_report().replace(
            "**Unestablished Propositions**: 4",
            "**Unestablished Propositions**: NONE",
        )
        errors = reg.validate_report_consistency(report_md)
        assert len(errors) > 0
        assert any("Unestablished" in str(e) for e in errors)


class TestRecoveryClasses:
    """Evidence debt recovery classes must be first-class objects."""

    def test_recovery_class_constants(self):
        assert RecoveryClass.RECOVERY_REQUIRED == "RECOVERY_REQUIRED"
        assert RecoveryClass.INDEPENDENT_VERIFICATION_REQUIRED == "INDEPENDENT_VERIFICATION_REQUIRED"
        assert RecoveryClass.SOURCE_UPGRADE_REQUIRED == "SOURCE_UPGRADE_REQUIRED"
        assert RecoveryClass.UNAVAILABLE_BY_CONSTRAINT == "UNAVAILABLE_BY_CONSTRAINT"

    def test_evidence_debt_dataclass(self):
        debt = EvidenceDebt(
            debt_id="P-08-005d-debt-1",
            proposition="P-08-005d",
            missingness="Royalty rate is confidential",
            recovery_class=RecoveryClass.UNAVAILABLE_BY_CONSTRAINT,
            severity="HIGH",
            recoverable=False,
            reason="Financial terms not publicly disclosed",
            recommended_action="Request under NDA",
        )
        assert debt.recovery_class == "UNAVAILABLE_BY_CONSTRAINT"
        assert debt.recoverable is False

    def test_ledger_debt_loaded_with_recovery_class(self):
        """P-08-005d debt must carry UNAVAILABLE_BY_CONSTRAINT from the ledger."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        prop = reg.get("P-08-005d")
        assert prop is not None
        assert len(prop.debt) == 1
        assert prop.debt[0].recovery_class == RecoveryClass.UNAVAILABLE_BY_CONSTRAINT
        assert prop.debt[0].recoverable is False

    def test_atomic_decomposition_loaded(self):
        """P-08-005 must decompose into P-08-005a..f."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        children = reg.atomic_children("P-08-005")
        assert [c.proposition_id for c in children] == [
            "P-08-005a", "P-08-005b", "P-08-005c",
            "P-08-005d", "P-08-005e", "P-08-005f",
        ]
        # Parent auto-derived state
        assert reg.state_of("P-08-005") == "PARTIALLY_ESTABLISHED"
        # Children states
        assert reg.state_of("P-08-005a") == "ESTABLISHED"
        assert reg.state_of("P-08-005d") == "NOT_ESTABLISHED"

    def test_unestablished_top_level_counts_parent_not_children(self):
        """Headline count must be 4: atomic children are sub-claims of a
        decomposed parent already counted (P-08-005 PARTIALLY_ESTABLISHED)."""
        ledger = _load_ledger()
        reg = PropositionRegistry(ledger)
        top = reg.unestablished_top_level()
        ids = [p.proposition_id for p in top]
        assert ids == ["P-03-003", "P-06-005", "P-07-001", "P-08-005"]
        # Children are NOT double-counted in the headline
        assert "P-08-005d" not in ids
        assert "P-08-005e" not in ids
        assert "P-08-005f" not in ids
        # But the full registry still sees them as unestablished
        full = reg.unestablished()
        assert len(full) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])