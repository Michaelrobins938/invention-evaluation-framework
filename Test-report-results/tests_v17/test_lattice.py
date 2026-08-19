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
