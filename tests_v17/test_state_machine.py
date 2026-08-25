"""v1.8 evidence-state controller tests.

The v1.7 controller collapsed *operational* failure into *epistemic*
exhaustion: ``request fails → BLOCKED → EXHAUSTED``. A rate limit, an
unavailable database, or an unattempted fallback was reported as if the
search had been completed. These tests pin the v1.8 invariant:

    **An avenue cannot become EXHAUSTED while an admissible recovery path
    remains unattempted.**

"Stopped searching" and "the evidence indicates absence" are radically
different propositions; the framework must make it impossible for downstream
scoring to confuse them.
"""

from engine_v17.models import Proposition, ResolutionState, ResearchExhaustion
from engine_v17.recovery import (
    FailureClass,
    RecoveryAttempt,
    classify_failure,
    is_terminal_exhaustion,
    recovery_paths_remaining,
    transition_state,
)
from engine_v17.execution import ExecutionLedger


def _patent_attempts(ledger=None, **overrides):
    """The five distinct recovery strategies the patent policy requires."""
    attempts = [
        RecoveryAttempt("primary_patent_database", "keyword", strategy_class="terminology"),
        RecoveryAttempt("primary_patent_database", "verified_classification", strategy_class="classification"),
        RecoveryAttempt("primary_patent_database", "citation_traversal", strategy_class="citation_lineage"),
        RecoveryAttempt("primary_patent_database", "family_traversal", strategy_class="family_continuity"),
        RecoveryAttempt("secondary_patent_database", "prosecution_history", strategy_class="prosecution_history"),
    ]
    if ledger is not None:
        for attempt in attempts:
            attempt.execution_id = ledger.record(
                "05", attempt.method, attempt.source, attempt.method).execution_id
    for k, v in overrides.items():
        for attempt in attempts:
            setattr(attempt, k, v)
    return attempts


def _exhaustion_record(proposition, attempts):
    return ResearchExhaustion(
        proposition_id=proposition.id,
        sources=["primary_patent_database", "secondary_patent_database"],
        methods=[a.method for a in attempts],
        coverage={"claims_checked": ["claim_1"], "limitations_checked": ["L1", "L2"]},
        results={"result_count": 0},
        failure_diagnosis="five strategies completed without admissible evidence",
        troubleshooting=[{"query": "patent search guidance", "source": "documentation"}],
        recovery_strategies=[a.to_dict() for a in attempts],
        alternate_routes_attempted=["secondary_patent_database"],
        recursive_recovery_completed=True,
        termination_basis="five distinct recovery strategies completed without admissible evidence",
    )


# ---------------------------------------------------------------------------
# classify_failure
# ---------------------------------------------------------------------------

def test_transient_rate_limit_is_not_epistemic_exhaustion():
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="rate_limited")) == FailureClass.TRANSIENT_FAILURE
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="timeout")) == FailureClass.TRANSIENT_FAILURE
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="service_unavailable")) == FailureClass.TRANSIENT_FAILURE


def test_source_unavailable_is_not_epistemic_exhaustion():
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="credential_required")) == FailureClass.SOURCE_UNAVAILABLE
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="permission_required")) == FailureClass.SOURCE_UNAVAILABLE
    assert classify_failure(RecoveryAttempt("a", "b", rejection_reason="source_blocked")) == FailureClass.SOURCE_UNAVAILABLE


def test_genuinely_exhausted_attempts_classify_as_epistemic():
    assert classify_failure(RecoveryAttempt("a", "b", result_count=0)) == FailureClass.EPISTEMIC_EXHAUSTION


# ---------------------------------------------------------------------------
# recovery_paths_remaining / is_terminal_exhaustion
# ---------------------------------------------------------------------------

def test_unattempted_required_path_means_not_terminal():
    attempts = _patent_attempts()[:2]  # only 2 of 5 required strategies
    from engine_v17.recovery import select_recovery_policy
    policy = select_recovery_policy(Proposition(id="P-05-001", claim="Claim 1 anticipation"))
    remaining = recovery_paths_remaining(attempts, policy)
    assert remaining, "unattempted required paths must remain"
    assert not is_terminal_exhaustion(attempts, policy)


def test_transient_failure_means_not_terminal():
    attempts = _patent_attempts(rejection_reason="rate_limited")
    from engine_v17.recovery import select_recovery_policy
    policy = select_recovery_policy(Proposition(id="P-05-001", claim="Claim 1 anticipation"))
    assert not is_terminal_exhaustion(attempts, policy)


def test_source_unavailable_means_not_terminal():
    attempts = _patent_attempts(rejection_reason="credential_required")
    from engine_v17.recovery import select_recovery_policy
    policy = select_recovery_policy(Proposition(id="P-05-001", claim="Claim 1 anticipation"))
    assert not is_terminal_exhaustion(attempts, policy)


def test_complete_epistemic_failure_is_terminal():
    attempts = _patent_attempts(result_count=0)
    from engine_v17.recovery import select_recovery_policy
    policy = select_recovery_policy(Proposition(id="P-05-001", claim="Claim 1 anticipation"))
    assert is_terminal_exhaustion(attempts, policy)


# ---------------------------------------------------------------------------
# transition_state
# ---------------------------------------------------------------------------

def test_transient_rate_limit_does_not_become_search_exhausted():
    """THE key regression test. A rate-limited avenue must route to
    ESCALATION_REQUIRED (retry/backoff), never to SEARCH_EXHAUSTED."""
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = _patent_attempts(rejection_reason="rate_limited")
    result = transition_state(proposition, attempts)
    assert result == ResolutionState.ESCALATION_REQUIRED, (
        "a transient rate limit must not be reported as search exhaustion")


def test_unavailable_source_does_not_become_search_exhausted():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = _patent_attempts(rejection_reason="permission_required")
    assert transition_state(proposition, attempts) == ResolutionState.ESCALATION_REQUIRED


def test_unattempted_fallback_does_not_become_search_exhausted():
    """Only 2 of 5 required strategies attempted — the fallback is unattempted,
    so the avenue is not exhausted."""
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = _patent_attempts()[:2]
    assert transition_state(proposition, attempts) == ResolutionState.ESCALATION_REQUIRED


def test_genuine_exhaustion_still_permitted_when_all_paths_tried():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    ledger = ExecutionLedger(run_id="RUN-05")
    attempts = _patent_attempts(ledger=ledger, result_count=0)
    proposition.recovery = _exhaustion_record(proposition, attempts)
    assert transition_state(proposition, attempts, ledger) == ResolutionState.SEARCH_EXHAUSTED


def test_transient_failure_records_operational_diagnosis():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = _patent_attempts(rejection_reason="rate_limited")
    transition_state(proposition, attempts)
    assert proposition.recovery is not None
    assert "transient" in proposition.recovery.failure_diagnosis.lower()


def test_source_unavailable_records_fallback_diagnosis():
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = _patent_attempts(rejection_reason="credential_required")
    transition_state(proposition, attempts)
    assert proposition.recovery is not None
    assert "source" in proposition.recovery.failure_diagnosis.lower() or "alternate" in proposition.recovery.failure_diagnosis.lower()


def test_no_confusion_between_stopped_searching_and_evidence_absence():
    """The framework-level assertion: a proposition whose search was stopped
    for an operational reason must never carry a terminal exhaustion
    disposition, because downstream scoring would otherwise read
    'we stopped searching' as 'the evidence indicates absence'."""
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    attempts = _patent_attempts(rejection_reason="rate_limited")
    transition_state(proposition, attempts)
    assert proposition.recovery.disposition != ResolutionState.SEARCH_EXHAUSTED
    assert proposition.recovery.disposition is None  # not terminal at all