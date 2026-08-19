# report-renderer/tests/test_lattice_contract.py
import json
import pytest
from contract import (
    EpistemicState, RecoveryState, Scope, PropositionRegistry,
)


def test_epistemic_state_has_canonical_values():
    assert EpistemicState.ESTABLISHED == "ESTABLISHED"
    assert EpistemicState.PARTIALLY_ESTABLISHED == "PARTIALLY_ESTABLISHED"
    assert EpistemicState.NOT_ESTABLISHED == "NOT_ESTABLISHED"
    assert EpistemicState.CONTRADICTED == "CONTRADICTED"


def test_legacy_partial_aliases_to_partially_established():
    assert EpistemicState.PARTIAL == EpistemicState.PARTIALLY_ESTABLISHED


def test_recovery_state_values():
    assert {r for r in RecoveryState} == {
        "NONE_REQUIRED", "SEARCH_PENDING", "ESCALATION_REQUIRED",
        "EXHAUSTED", "UNAVAILABLE_BY_CONSTRAINT",
    }


def test_scope_values():
    assert {s for s in Scope} == {
        "TARGET_PATENT", "PATENT_FAMILY", "TECHNOLOGY_LINEAGE",
        "COMMERCIAL_PRODUCT", "ASSIGNEE_PORTFOLIO", "MARKET", "REGULATORY",
    }


def test_registry_loads_new_lattice_fields():
    ledger = {"proposition_ledger": {
        "P-08-005d": {
            "claim": "Confidential royalty rate",
            "epistemic_state": "NOT_ESTABLISHED",
            "recovery_state": "UNAVAILABLE_BY_CONSTRAINT",
            "scope": "COMMERCIAL_PRODUCT",
        },
    }}
    reg = PropositionRegistry(ledger)
    prop = reg.get("P-08-005d")
    assert prop.state == "NOT_ESTABLISHED"
    assert prop.recovery_state == "UNAVAILABLE_BY_CONSTRAINT"
    assert prop.scope == "COMMERCIAL_PRODUCT"


def test_registry_migrates_legacy_status():
    ledger = {"proposition_ledger": {
        "P-03-003": {"claim": "yield", "status": "ESCALATION_REQUIRED"},
    }}
    reg = PropositionRegistry(ledger)
    prop = reg.get("P-03-003")
    assert prop.state == "NOT_ESTABLISHED"
    assert prop.recovery_state == "ESCALATION_REQUIRED"