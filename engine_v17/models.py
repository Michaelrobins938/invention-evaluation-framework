"""Typed state models for the v1.7 evidence-recovery control layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class UnknownType(str, Enum):
    NOT_SEARCHED = "not_searched"
    INSUFFICIENT_QUERY = "insufficient_query"
    UNAVAILABLE_SOURCE = "unavailable_source"
    AMBIGUOUS_IDENTITY = "ambiguous_identity"
    MISSING_PRIMARY_RECORD = "missing_primary_record"
    PROPRIETARY_INFORMATION = "proprietary_information"
    LEGALLY_SENSITIVE = "legally_sensitive"
    CONTRADICTORY_SOURCES = "contradictory_sources"
    SEARCH_EXHAUSTED = "search_exhausted"


class ResolutionState(str, Enum):
    ESTABLISHED = "established"
    UNRESOLVED = "unresolved"
    ESCALATION_REQUIRED = "escalation_required"
    SEARCH_EXHAUSTED = "search_exhausted"
    BLOCKED = "blocked"
    MIGRATION_REQUIRED = "migration_required"


class FailureClass(str, Enum):
    """The *operational* cause of a recovery failure.

    v1.8 separates these deliberately. A rate limit, unavailable database,
    failed endpoint, or unattempted fallback is **not** the same epistemic
    condition as genuine exhaustion, and the framework must not collapse them:

      TRANSIENT_FAILURE  → retry/backoff is admissible
      SOURCE_UNAVAILABLE → an alternate source is admissible
      SOURCE_EXHAUSTED  → every admissible source has been tried and failed
      EPISTEMIC_EXHAUSTION → the evidence genuinely does not exist

    The old code mapped ``request fails → BLOCKED → EXHAUSTED``, which let a
    transient rate limit be reported as if the search had been completed.
    """
    TRANSIENT_FAILURE = "transient_failure"
    SOURCE_UNAVAILABLE = "source_unavailable"
    SOURCE_EXHAUSTED = "source_exhausted"
    EPISTEMIC_EXHAUSTION = "epistemic_exhaustion"
    UNKNOWN = "unknown"


# Rejection reasons that are *operational* — they admit retry or fallback.
TRANSIENT_REASONS = frozenset({
    "rate_limited", "timeout", "service_unavailable", "network_error",
    "server_error", "request_throttled", "temporary_outage",
})
# Rejection reasons that point at a *source* problem, not a transient one.
SOURCE_UNAVAILABLE_REASONS = frozenset({
    "credential_required", "permission_required", "source_blocked",
    "source_offline", "endpoint_deprecated", "database_unavailable",
})


class EvidenceState(str, Enum):
    CONFIRMED_PRESENT = "CONFIRMED PRESENT"
    CONFIRMED_ABSENT = "CONFIRMED ABSENT"
    WORK_QUEUE = "WORK QUEUE"
    EXCLUDED = "EXCLUDED"


@dataclass
class ResearchExhaustion:
    proposition_id: str
    sources: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    remaining_uncertainty: list[str] = field(default_factory=list)
    disposition: ResolutionState | None = None
    failure_diagnosis: str = ""
    troubleshooting: list[dict[str, Any]] = field(default_factory=list)
    recovery_strategies: list[dict[str, Any]] = field(default_factory=list)
    alternate_routes_attempted: list[str] = field(default_factory=list)
    recursive_recovery_completed: bool = False
    blocked_source_indispensable: bool = False
    termination_basis: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchExhaustion":
        attempted = data.get("attempted", {})
        return cls(
            proposition_id=data["proposition_id"],
            sources=list(data.get("sources", attempted.get("sources", []))),
            methods=list(data.get("methods", attempted.get("methods", []))),
            coverage=dict(data.get("coverage", attempted.get("coverage", {}))),
            results=dict(data.get("results", {})),
            remaining_uncertainty=list(data.get("remaining_uncertainty", [])),
            disposition=_resolution(data.get("disposition")),
            failure_diagnosis=data.get("failure_diagnosis", ""),
            troubleshooting=list(data.get("troubleshooting", [])),
            recovery_strategies=list(data.get("recovery_strategies", [])),
            alternate_routes_attempted=list(data.get("alternate_routes_attempted", [])),
            recursive_recovery_completed=bool(data.get("recursive_recovery_completed", False)),
            blocked_source_indispensable=bool(data.get("blocked_source_indispensable", False)),
            termination_basis=data.get("termination_basis", ""),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.sources:
            errors.append("attempted.sources")
        if not self.methods:
            errors.append("attempted.methods")
        if not self.coverage:
            errors.append("attempted.coverage")
        if self.disposition == ResolutionState.SEARCH_EXHAUSTED:
            if "qualifying_references" not in self.results and "result_count" not in self.results:
                errors.append("results")
            errors.extend(self._validate_recovery_contract())
        if self.disposition == ResolutionState.BLOCKED:
            errors.extend(self._validate_recovery_contract())
            if not self.blocked_source_indispensable:
                errors.append("blocked_source_indispensable")
        return errors

    def _validate_recovery_contract(self) -> list[str]:
        errors: list[str] = []
        if not self.failure_diagnosis:
            errors.append("failure_diagnosis")
        if not self.troubleshooting:
            errors.append("online_troubleshooting")
        if len(self.recovery_strategies) < 5:
            errors.append("minimum_five_strategies")
        classes = {
            strategy.get("strategy_class")
            for strategy in self.recovery_strategies
            if strategy.get("strategy_class")
        }
        if len(classes) < 4:
            errors.append("minimum_four_strategy_classes")
        if any(not strategy.get("executed", False) for strategy in self.recovery_strategies):
            errors.append("unexecuted_recovery_strategy")
        if not self.recursive_recovery_completed:
            errors.append("recursive_recovery")
        if not self.termination_basis:
            errors.append("termination_basis")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposition_id": self.proposition_id,
            "attempted": {
                "sources": self.sources,
                "methods": self.methods,
                "coverage": self.coverage,
            },
            "results": self.results,
            "remaining_uncertainty": self.remaining_uncertainty,
            "disposition": self.disposition.value if self.disposition else None,
            "failure_diagnosis": self.failure_diagnosis,
            "troubleshooting": self.troubleshooting,
            "recovery_strategies": self.recovery_strategies,
            "alternate_routes_attempted": self.alternate_routes_attempted,
            "recursive_recovery_completed": self.recursive_recovery_completed,
            "blocked_source_indispensable": self.blocked_source_indispensable,
            "termination_basis": self.termination_basis,
        }


@dataclass
class EvidenceLeverage:
    proposition_id: str
    importance: str = "low"
    affected_nodes: list[str] = field(default_factory=list)
    resolution_value: str = "low"
    recovery_priority: int = 99

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Proposition:
    id: str
    claim: str = ""
    state: ResolutionState = ResolutionState.UNRESOLVED
    evidence_state: EvidenceState = EvidenceState.WORK_QUEUE
    unknown_type: UnknownType | None = None
    search_completeness: str = "incomplete"
    evidence_strength: str = "insufficient"
    confidence: str = "low"
    blockers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    downstream_effects: list[str] = field(default_factory=list)
    recovery: ResearchExhaustion | None = None
    evidence_sufficiency_passed: bool = False
    migration_metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Proposition":
        raw_state = str(data.get("state", ResolutionState.UNRESOLVED.value)).lower()
        if raw_state == "exhausted":
            state = ResolutionState.MIGRATION_REQUIRED
            migration = dict(data.get("migration_metadata", {}))
            migration["legacy_state"] = "EXHAUSTED"
        else:
            state = _resolution(raw_state) or ResolutionState.UNRESOLVED
            migration = dict(data.get("migration_metadata", {}))
        raw_unknown = data.get("unknown_type")
        return cls(
            id=data["id"],
            claim=data.get("claim", ""),
            state=state,
            evidence_state=_evidence(data.get("evidence_state")),
            unknown_type=_unknown(raw_unknown),
            search_completeness=data.get("search_completeness", "incomplete"),
            evidence_strength=data.get("evidence_strength", "insufficient"),
            confidence=data.get("confidence", "low"),
            blockers=list(data.get("blockers", [])),
            dependencies=list(data.get("dependencies", [])),
            downstream_effects=list(data.get("downstream_effects", [])),
            recovery=ResearchExhaustion.from_dict(data["recovery"]) if data.get("recovery") else None,
            evidence_sufficiency_passed=bool(data.get("evidence_sufficiency_passed", False)),
            migration_metadata=migration,
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
            "id": self.id,
            "claim": self.claim,
            "state": self.state.value,
            "evidence_state": self.evidence_state.value,
            "unknown_type": self.unknown_type.value if self.unknown_type else None,
            "search_completeness": self.search_completeness,
            "evidence_strength": self.evidence_strength,
            "confidence": self.confidence,
            "blockers": self.blockers,
            "dependencies": self.dependencies,
            "downstream_effects": self.downstream_effects,
            "evidence_sufficiency_passed": self.evidence_sufficiency_passed,
            "migration_metadata": self.migration_metadata,
        }
        if self.recovery:
            result["recovery"] = self.recovery.to_dict()
        return result


def _resolution(value: Any) -> ResolutionState | None:
    if value is None:
        return None
    try:
        return ResolutionState(str(value).lower())
    except ValueError:
        return None


def _unknown(value: Any) -> UnknownType | None:
    if value is None:
        return None
    try:
        return UnknownType(str(value).lower())
    except ValueError:
        return None


def _evidence(value: Any) -> EvidenceState:
    if value is None:
        return EvidenceState.WORK_QUEUE
    normalized = str(value).upper().replace("_", " ")
    for state in EvidenceState:
        if state.value == normalized:
            return state
    return EvidenceState.WORK_QUEUE
