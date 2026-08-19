from engine_v17.models import Proposition, ResolutionState, ResearchExhaustion
from engine_v17.recovery import RecoveryAttempt, transition_state
from engine_v17.compiler import compile_v17_artifacts
from engine_v17.execution import ExecutionLedger


def test_exhaustion_requires_sources_methods_and_coverage():
    record = ResearchExhaustion.from_dict({"proposition_id": "P-05-001"})
    assert "attempted.sources" in record.validate()
    assert "attempted.methods" in record.validate()
    assert "attempted.coverage" in record.validate()


def test_legacy_exhausted_is_not_active_v17_state():
    proposition = Proposition.from_dict({"id": "P-07-001", "state": "EXHAUSTED"})
    assert proposition.state == ResolutionState.MIGRATION_REQUIRED


def test_unsearched_proposition_requires_escalation():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    assert transition_state(proposition, []) == ResolutionState.ESCALATION_REQUIRED


def test_complete_empty_patent_search_can_be_search_exhausted():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    ledger = ExecutionLedger(run_id="RUN-05")
    attempts = [
        RecoveryAttempt("primary_patent_database", "keyword", strategy_class="terminology"),
        RecoveryAttempt("primary_patent_database", "verified_classification", strategy_class="classification"),
        RecoveryAttempt("primary_patent_database", "citation_traversal", strategy_class="citation_lineage"),
        RecoveryAttempt("primary_patent_database", "family_traversal", strategy_class="family_continuity"),
        RecoveryAttempt("secondary_patent_database", "prosecution_history", strategy_class="prosecution_history"),
    ]
    for attempt in attempts:
        attempt.execution_id = ledger.record("05", attempt.method, attempt.source, attempt.method).execution_id
    proposition.recovery = ResearchExhaustion(
        proposition_id=proposition.id,
        sources=["primary_patent_database", "secondary_patent_database"],
        methods=[attempt.method for attempt in attempts],
        coverage={"claims_checked": ["claim_1"], "limitations_checked": ["L1", "L2"]},
        results={"result_count": 0},
        failure_diagnosis="historical terminology and lineage may be indexed separately",
        troubleshooting=[{"query": "patent search guidance", "source": "database documentation"}],
        recovery_strategies=[attempt.to_dict() for attempt in attempts],
        alternate_routes_attempted=["secondary_patent_database"],
        recursive_recovery_completed=True,
        termination_basis="five distinct recovery strategies completed without admissible evidence",
    )
    assert transition_state(proposition, attempts, ledger) == ResolutionState.SEARCH_EXHAUSTED


def test_blocked_source_creates_escalation_obligation():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = [
        RecoveryAttempt(
            "primary_patent_database",
            "keyword",
            strategy_class="terminology",
            rejection_reason="source_blocked",
        )
    ]
    assert transition_state(proposition, attempts) == ResolutionState.ESCALATION_REQUIRED


def test_positive_result_requires_sufficiency_gate():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = [
        RecoveryAttempt("primary_patent_database", "keyword", result_count=1, strategy_class="terminology")
    ]
    assert transition_state(proposition, attempts) == ResolutionState.ESCALATION_REQUIRED


def test_established_requires_explicit_sufficiency_gate():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    proposition.evidence_sufficiency_passed = True
    attempts = [
        RecoveryAttempt("primary_patent_database", "keyword", result_count=1, strategy_class="terminology")
    ]
    assert transition_state(proposition, attempts) == ResolutionState.ESTABLISHED


def test_exhaustion_requires_five_distinct_recovery_classes():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    proposition.recovery = ResearchExhaustion(
        proposition_id=proposition.id,
        sources=["primary_patent_database", "secondary_patent_database"],
        methods=["keyword", "verified_classification"],
        coverage={"claims_checked": ["claim_1"]},
        results={"result_count": 0},
        failure_diagnosis="query terminology mismatch",
        troubleshooting=[{"query": "historical patent terminology", "source": "documentation"}],
        recovery_strategies=[{"strategy_class": "terminology", "executed": True}] * 5,
        alternate_routes_attempted=["secondary_patent_database"],
        recursive_recovery_completed=True,
        termination_basis="insufficient strategy diversity",
    )
    attempts = [
        RecoveryAttempt("primary_patent_database", f"method-{index}", strategy_class="terminology")
        for index in range(5)
    ]
    assert transition_state(proposition, attempts) == ResolutionState.ESCALATION_REQUIRED


def test_compiler_rejects_established_proposition_without_sufficiency_gate(tmp_path):
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation", state=ResolutionState.ESTABLISHED)
    try:
        compile_v17_artifacts([proposition], tmp_path)
    except ValueError as error:
        assert "evidence sufficiency gate not passed" in str(error)
    else:
        raise AssertionError("compiler accepted unsupported established proposition")
