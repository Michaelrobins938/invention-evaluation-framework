# Test-report-results/tests_v17/test_lattice.py
from engine_v17.models import (
    EpistemicState, RecoveryState, Scope, ResolutionState,
    lattice_from_legacy, legacy_from_lattice,
)


def test_legacy_established_maps_to_established_none_required():
    assert lattice_from_legacy(ResolutionState.ESTABLISHED) == (
        EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED)


def test_legacy_escalation_maps_to_not_established_escalation():
    assert lattice_from_legacy(ResolutionState.ESCALATION_REQUIRED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED)


def test_legacy_search_exhausted_maps_to_exhausted():
    assert lattice_from_legacy(ResolutionState.SEARCH_EXHAUSTED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED)


def test_legacy_unresolved_maps_to_search_pending():
    assert lattice_from_legacy(ResolutionState.UNRESOLVED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING)


def test_legacy_blocked_maps_to_escalation():
    assert lattice_from_legacy(ResolutionState.BLOCKED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED)


def test_legacy_migration_required_maps_to_search_pending():
    assert lattice_from_legacy(ResolutionState.MIGRATION_REQUIRED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING)


def test_round_trip_established():
    assert legacy_from_lattice(EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED) == ResolutionState.ESTABLISHED


def test_round_trip_exhausted():
    assert legacy_from_lattice(EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED) == ResolutionState.SEARCH_EXHAUSTED


def test_scope_enum_has_all_seven_values():
    assert {s.value for s in Scope} == {
        "TARGET_PATENT", "PATENT_FAMILY", "TECHNOLOGY_LINEAGE",
        "COMMERCIAL_PRODUCT", "ASSIGNEE_PORTFOLIO", "MARKET", "REGULATORY",
    }


# --- Task A2: Proposition carries lattice + scope ---

from engine_v17.models import Proposition


def test_proposition_from_legacy_state_migrates_to_lattice():
    # "search_exhausted" is the actual ResolutionState value that maps to
    # RecoveryState.EXHAUSTED. The legacy "exhausted" shorthand is migrated
    # to MIGRATION_REQUIRED by from_dict (v1.7 quirk).
    p = Proposition.from_dict({"id": "P-07-001", "state": "search_exhausted"})
    assert p.epistemic_state == EpistemicState.NOT_ESTABLISHED
    assert p.recovery_state == RecoveryState.EXHAUSTED


def test_proposition_from_new_fields_round_trips():
    p = Proposition.from_dict({
        "id": "P-08-005d",
        "claim": "Confidential royalty rate",
        "epistemic_state": "NOT_ESTABLISHED",
        "recovery_state": "UNAVAILABLE_BY_CONSTRAINT",
        "scope": "COMMERCIAL_PRODUCT",
    })
    assert p.epistemic_state == EpistemicState.NOT_ESTABLISHED
    assert p.recovery_state == RecoveryState.UNAVAILABLE_BY_CONSTRAINT
    assert p.scope == Scope.COMMERCIAL_PRODUCT
    d = p.to_dict()
    assert d["epistemic_state"] == "NOT_ESTABLISHED"
    assert d["recovery_state"] == "UNAVAILABLE_BY_CONSTRAINT"
    assert d["scope"] == "COMMERCIAL_PRODUCT"
    # legacy shim uses the repo's lowercase ResolutionState values
    assert d["state"] == "unresolved"


def test_proposition_from_lattice_fields_sets_state_shim():
    p = Proposition.from_dict({
        "id": "P-03-003",
        "claim": "yield",
        "epistemic_state": "NOT_ESTABLISHED",
        "recovery_state": "ESCALATION_REQUIRED",
    })
    assert p.state == ResolutionState.ESCALATION_REQUIRED
    assert p.epistemic_state == EpistemicState.NOT_ESTABLISHED
    assert p.recovery_state == RecoveryState.ESCALATION_REQUIRED


def test_proposition_default_scope_is_target_patent():
    p = Proposition(id="P-03-001", claim="y")
    assert p.scope == Scope.TARGET_PATENT


# --- Task A3: transition_lattice in recovery.py ---

from engine_v17.recovery import transition_lattice, RecoveryAttempt
from engine_v17.execution import ExecutionLedger


def test_transition_lattice_no_attempts_is_escalation():
    p = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    assert transition_lattice(p, []) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED)


def test_transition_lattice_evidence_passed_is_established():
    p = Proposition(id="P-03-001", claim="3D array", evidence_sufficiency_passed=True)
    attempts = [RecoveryAttempt("primary_patent_database", "keyword", result_count=3)]
    assert transition_lattice(p, attempts) == (
        EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED)


def test_transition_lattice_terminal_exhaustion():
    from engine_v17.models import ResearchExhaustion
    p = Proposition(id="P-05-001", claim="Claim 1 anticipation",
                    recovery=ResearchExhaustion(
                        proposition_id="P-05-001",
                        sources=["primary_patent_database", "secondary_patent_database"],
                        methods=["keyword", "verified_classification",
                                 "citation_traversal", "family_traversal"],
                        coverage={"claims_checked": ["claim_1"], "limitations_checked": ["L1", "L2"]},
                        results={"result_count": 0},
                        failure_diagnosis="historical terminology and lineage may be indexed separately",
                        troubleshooting=[{"query": "patent search guidance", "source": "database documentation"}],
                        recovery_strategies=[
                            {"strategy_class": "terminology", "executed": True},
                            {"strategy_class": "classification", "executed": True},
                            {"strategy_class": "citation_lineage", "executed": True},
                            {"strategy_class": "family", "executed": True},
                            {"strategy_class": "terminology", "executed": True},
                        ],
                        alternate_routes_attempted=["secondary_patent_database"],
                        recursive_recovery_completed=True,
                        termination_basis="five distinct recovery strategies completed without admissible evidence"))
    ledger = ExecutionLedger(run_id="RUN-05")
    attempts = [
        RecoveryAttempt("primary_patent_database", "keyword", result_count=0, strategy_class="terminology"),
        RecoveryAttempt("primary_patent_database", "verified_classification", result_count=0, strategy_class="classification"),
        RecoveryAttempt("primary_patent_database", "citation_traversal", result_count=0, strategy_class="citation_lineage"),
        RecoveryAttempt("primary_patent_database", "family_traversal", result_count=0, strategy_class="family"),
        RecoveryAttempt("secondary_patent_database", "keyword", result_count=0, strategy_class="terminology"),
        RecoveryAttempt("secondary_patent_database", "verified_classification", result_count=0, strategy_class="classification"),
        RecoveryAttempt("secondary_patent_database", "citation_traversal", result_count=0, strategy_class="citation_lineage"),
        RecoveryAttempt("secondary_patent_database", "family_traversal", result_count=0, strategy_class="family"),
    ]
    for a in attempts:
        rec = ledger.record(
            phase_id="patent",
            action_type=a.method,
            source=a.source,
            query="",
            result_count=a.result_count,
            outcome="",
            candidate_evidence=False,
            evidence_sufficiency=False,
        )
        a.execution_id = rec.execution_id
    assert transition_lattice(p, attempts, ledger) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED)


# --- Task A4: evidence debt = recoverable items only ---

from engine_v17.constraints import calculate_evidence_debt


def test_evidence_debt_excludes_unavailable_by_constraint():
    props = [
        Proposition(id="P-08-005d", claim="royalty",
                    epistemic_state=EpistemicState.NOT_ESTABLISHED,
                    recovery_state=RecoveryState.UNAVAILABLE_BY_CONSTRAINT),
        Proposition(id="P-03-003", claim="yield",
                    epistemic_state=EpistemicState.NOT_ESTABLISHED,
                    recovery_state=RecoveryState.ESCALATION_REQUIRED),
        Proposition(id="P-03-001", claim="3D array",
                    epistemic_state=EpistemicState.ESTABLISHED,
                    recovery_state=RecoveryState.NONE_REQUIRED),
    ]
    debt = calculate_evidence_debt(props)
    ids = {d.proposition_id for d in debt}
    assert ids == {"P-03-003"}


def test_evidence_debt_includes_search_pending():
    props = [
        Proposition(id="P-06-005", claim="market share",
                    epistemic_state=EpistemicState.PARTIALLY_ESTABLISHED,
                    recovery_state=RecoveryState.SEARCH_PENDING),
    ]
    debt = calculate_evidence_debt(props)
    assert [d.proposition_id for d in debt] == ["P-06-005"]


# --- Task A6: migrate_v18_ledger ---

from engine_v17.migration import migrate_v18_ledger


def test_migrate_v18_ledger_adds_lattice_fields():
    ledger = {"proposition_ledger": {
        "P-03-003": {"claim": "yield", "status": "ESCALATION_REQUIRED"},
        "P-08-005d": {"claim": "royalty", "status": "NOT_ESTABLISHED",
                      "recovery_state": "UNAVAILABLE_BY_CONSTRAINT"},
    }}
    out = migrate_v18_ledger(ledger)
    p3 = out["proposition_ledger"]["P-03-003"]
    assert p3["epistemic_state"] == "NOT_ESTABLISHED"
    assert p3["recovery_state"] == "ESCALATION_REQUIRED"
    assert p3["scope"] == "TARGET_PATENT"
    assert p3["status"] == "ESCALATION_REQUIRED"  # legacy kept
    d = out["proposition_ledger"]["P-08-005d"]
    assert d["recovery_state"] == "UNAVAILABLE_BY_CONSTRAINT"
    assert d["epistemic_state"] == "NOT_ESTABLISHED"
