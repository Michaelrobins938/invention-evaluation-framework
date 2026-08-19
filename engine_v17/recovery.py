"""Evidence recovery policies and terminal-state controls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import (
    EpistemicState,
    EvidenceLeverage,
    FailureClass,
    Proposition,
    RecoveryState,
    ResolutionState,
    ResearchExhaustion,
    SOURCE_UNAVAILABLE_REASONS,
    TRANSIENT_REASONS,
    UnknownType,
    lattice_from_legacy,
)
from .execution import ExecutionLedger


def classify_failure(attempt: RecoveryAttempt) -> FailureClass:
    """Classify *why* a recovery attempt failed.

    This is the invariant the v1.8 controller enforces:

      **An avenue cannot become EXHAUSTED while an admissible recovery path
      remains unattempted.**

    A rate limit is not evidence absence. A failed endpoint is not evidence
    absence. Only when every admissible source has been tried and failed may
    the proposition be dispositioned as exhausted.
    """
    reason = (attempt.rejection_reason or "").strip().lower()
    if reason in TRANSIENT_REASONS:
        return FailureClass.TRANSIENT_FAILURE
    if reason in SOURCE_UNAVAILABLE_REASONS:
        return FailureClass.SOURCE_UNAVAILABLE
    if reason:
        return FailureClass.SOURCE_EXHAUSTED
    if attempt.result_count is not None and attempt.result_count <= 0:
        return FailureClass.EPISTEMIC_EXHAUSTION
    return FailureClass.UNKNOWN


def recovery_paths_remaining(
    attempts: list[RecoveryAttempt],
    policy: RecoveryPolicy,
) -> list[str]:
    """Return the admissible recovery paths that have NOT been attempted.

    A path is admissible if it is a required method/source pair from the
    policy. The controller invariant is:

        ``recovery_paths_remaining`` non-empty  →  NOT EXHAUSTED

    This is what prevents ``request fails → BLOCKED → EXHAUSTED``.
    """
    attempted_methods = {a.method for a in attempts}
    attempted_sources = {a.source for a in attempts}
    remaining: list[str] = []
    for source in policy.required_sources:
        for method in policy.required_methods:
            if method not in attempted_methods or source not in attempted_sources:
                remaining.append(f"{source}:{method}")
    return remaining


def is_terminal_exhaustion(
    attempts: list[RecoveryAttempt],
    policy: RecoveryPolicy,
) -> bool:
    """True only when every admissible recovery path has been attempted AND
    every attempt failed for an epistemic (not operational) reason."""
    if recovery_paths_remaining(attempts, policy):
        return False
    classes = {classify_failure(a) for a in attempts}
    # A transient or source-unavailable failure on any attempted path means
    # the avenue is recoverable, not exhausted.
    if classes & {FailureClass.TRANSIENT_FAILURE, FailureClass.SOURCE_UNAVAILABLE}:
        return False
    return True


@dataclass(frozen=True)
class RecoveryPolicy:
    name: str
    required_methods: tuple[str, ...]
    required_sources: tuple[str, ...]
    coverage_fields: tuple[str, ...] = ("claims_checked", "limitations_checked")


POLICIES = {
    "patent": RecoveryPolicy(
        "patent", ("keyword", "verified_classification", "citation_traversal", "family_traversal"),
        ("primary_patent_database", "secondary_patent_database"),
    ),
    "status": RecoveryPolicy(
        "status", ("identity_resolution", "maintenance_review", "assignment_review"),
        ("official_status_record", "assignment_record"), ("jurisdiction", "critical_dates"),
    ),
    "market": RecoveryPolicy(
        "market", ("population_model", "economic_proxy", "adoption_barrier_review"),
        ("public_health_source", "industry_source"), ("geography", "date_range"),
    ),
    "literature": RecoveryPolicy(
        "literature", ("keyword", "citation_traversal", "contradiction_search"),
        ("scholarly_database", "technical_database"),
    ),
    "commercial": RecoveryPolicy(
        "commercial", ("product_trace", "regulatory_trace", "company_history"),
        ("company_source", "regulatory_source", "clinical_source"),
    ),
    "partner": RecoveryPolicy(
        "partner", ("ownership_review", "capability_review", "contact_verification"),
        ("assignment_source", "company_source"),
    ),
}


@dataclass
class RecoveryAttempt:
    source: str
    method: str
    result_count: int | None = None
    rejection_reason: str | None = None
    coverage: dict[str, object] = field(default_factory=dict)
    strategy_class: str = ""
    action: str = ""
    executed: bool = True
    failure_diagnosis: str = ""
    execution_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "method": self.method,
            "result_count": self.result_count,
            "rejection_reason": self.rejection_reason,
            "coverage": self.coverage,
            "strategy_class": self.strategy_class,
            "action": self.action,
            "executed": self.executed,
            "failure_diagnosis": self.failure_diagnosis,
            "execution_id": self.execution_id,
        }


def classify_missingness(proposition: Proposition) -> UnknownType:
    if proposition.unknown_type:
        return proposition.unknown_type
    if proposition.search_completeness == "incomplete":
        return UnknownType.NOT_SEARCHED
    if proposition.blockers:
        return UnknownType.UNAVAILABLE_SOURCE
    return UnknownType.SEARCH_EXHAUSTED


def score_evidence_leverage(proposition: Proposition, graph: dict[str, Iterable[str]] | None = None) -> EvidenceLeverage:
    affected = list(proposition.downstream_effects)
    if graph and proposition.id in graph:
        affected = sorted(set(affected).union(graph[proposition.id]))
    critical_terms = {"anticipation", "patentability", "legal_leverage", "investor_recommendation"}
    critical = bool(critical_terms.intersection(affected))
    importance = "critical" if critical else ("moderate" if affected else "low")
    return EvidenceLeverage(
        proposition_id=proposition.id,
        importance=importance,
        affected_nodes=affected,
        resolution_value="high" if critical else ("moderate" if affected else "low"),
        recovery_priority=1 if critical else (10 if affected else 99),
    )


def select_recovery_policy(proposition: Proposition) -> RecoveryPolicy:
    text = f"{proposition.id} {proposition.claim}".lower()
    if any(term in text for term in ("anticipat", "prior art", "novelty", "obvious")):
        return POLICIES["patent"]
    if any(term in text for term in ("status", "maintenance", "expiration", "enforce")):
        return POLICIES["status"]
    if any(term in text for term in ("market", "revenue", "patient", "reimbursement")):
        return POLICIES["market"]
    if any(term in text for term in ("literature", "paper", "engineering")):
        return POLICIES["literature"]
    if any(term in text for term in ("product", "clinical", "commercial")):
        return POLICIES["commercial"]
    return POLICIES["partner"]


def validate_search_exhaustion(proposition: Proposition) -> list[str]:
    if not proposition.recovery:
        return ["recovery"]
    return proposition.recovery.validate()


def transition_lattice(
    proposition: Proposition,
    attempts: list[RecoveryAttempt],
    execution_ledger: ExecutionLedger | None = None,
) -> tuple[EpistemicState, RecoveryState]:
    """v1.9 canonical transition: returns (epistemic, recovery) separately.

    The legacy single-axis state conflated 'what we know' with 'what we can
    still do'. This function keeps the two axes distinct:
      - epistemic: ESTABLISHED / PARTIALLY_ESTABLISHED / NOT_ESTABLISHED / CONTRADICTED
      - recovery:  NONE_REQUIRED / SEARCH_PENDING / ESCALATION_REQUIRED / EXHAUSTED / UNAVAILABLE_BY_CONSTRAINT
    """
    legacy = transition_state(proposition, attempts, execution_ledger)
    return lattice_from_legacy(legacy)


def transition_state(
    proposition: Proposition,
    attempts: list[RecoveryAttempt],
    execution_ledger: ExecutionLedger | None = None,
) -> ResolutionState:
    if not attempts:
        return ResolutionState.ESCALATION_REQUIRED
    if any((a.result_count or 0) > 0 for a in attempts):
        return ResolutionState.ESTABLISHED if proposition.evidence_sufficiency_passed else ResolutionState.ESCALATION_REQUIRED

    policy = select_recovery_policy(proposition)
    methods = {a.method for a in attempts}
    sources = {a.source for a in attempts}

    # ---- v1.8 invariant: an avenue cannot become EXHAUSTED while an admissible
    # recovery path remains unattempted. A transient rate limit or an
    # unattempted fallback is NOT evidence absence, so it routes to
    # ESCALATION_REQUIRED (the controller's job) rather than a terminal state.
    remaining = recovery_paths_remaining(attempts, policy)
    failure_classes = {classify_failure(a) for a in attempts}
    has_transient = bool(failure_classes & {FailureClass.TRANSIENT_FAILURE})
    has_source_unavailable = bool(failure_classes & {FailureClass.SOURCE_UNAVAILABLE})

    if remaining or has_transient or has_source_unavailable:
        if not proposition.recovery:
            # Auto-create the recovery record so the operational diagnosis is
            # recorded rather than silently lost. A transient failure with no
            # record would otherwise look identical to "never searched".
            proposition.recovery = ResearchExhaustion(
                proposition_id=proposition.id,
                sources=sorted(sources),
                methods=sorted(methods),
                coverage={},
                results={"result_count": 0},
            )
        # Record the operational diagnosis so the controller can retry or
        # fall back; never pretend the search was completed.
        if has_transient:
            proposition.recovery.failure_diagnosis = (
                proposition.recovery.failure_diagnosis
                or "transient failure; retry/backoff pending")
        elif has_source_unavailable:
            proposition.recovery.failure_diagnosis = (
                proposition.recovery.failure_diagnosis
                or "source unavailable; alternate source pending")
        else:
            proposition.recovery.failure_diagnosis = (
                proposition.recovery.failure_diagnosis
                or "required recovery path not attempted")
        return ResolutionState.ESCALATION_REQUIRED

    # Only reachable when every admissible path was attempted and every attempt
    # failed for an epistemic reason.
    if not proposition.recovery:
        return ResolutionState.ESCALATION_REQUIRED
    proposition.recovery.disposition = ResolutionState.SEARCH_EXHAUSTED
    recovery_errors = proposition.recovery.validate()
    if not recovery_errors and execution_ledger is None:
        recovery_errors.append("execution_ledger")
    if not recovery_errors and any(
        not attempt.execution_id or not execution_ledger.is_executed(attempt.execution_id)
        for attempt in attempts
    ):
        recovery_errors.append("unverified_execution_record")
    if recovery_errors:
        proposition.recovery.disposition = None
        return ResolutionState.ESCALATION_REQUIRED
    return ResolutionState.SEARCH_EXHAUSTED
