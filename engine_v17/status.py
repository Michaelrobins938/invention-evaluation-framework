"""Separate execution status from evidence status.

Execution complete != evidence sufficient. This module makes the distinction
machine-checkable and prevents collapsing into generic SUCCESS.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExecutionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    COMPLETED_WITH_EVIDENCE_DEBT = "COMPLETED_WITH_EVIDENCE_DEBT"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class EvidenceStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    PARTIALLY_SUFFICIENT = "PARTIALLY_SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    CONTRADICTED = "CONTRADICTED"
    UNAVAILABLE = "UNAVAILABLE"
    UNAVAILABLE_BY_CONSTRAINT = "UNAVAILABLE_BY_CONSTRAINT"
    ESCALATED = "ESCALATED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


@dataclass(frozen=True)
class CombinedStatus:
    """The two orthogonal statuses for a run or proposition."""

    execution: ExecutionStatus
    evidence: EvidenceStatus
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution": self.execution.value,
            "evidence": self.evidence.value,
            "detail": self.detail,
        }

    @property
    def is_execution_complete(self) -> bool:
        return self.execution in (ExecutionStatus.COMPLETE, ExecutionStatus.COMPLETED_WITH_EVIDENCE_DEBT)

    @property
    def is_evidence_sufficient(self) -> bool:
        return self.evidence == EvidenceStatus.SUFFICIENT

    def is_valid_conclusion(self) -> bool:
        """A conclusion is valid only if execution completed AND evidence sufficient."""
        return self.is_execution_complete and self.is_evidence_sufficient


# Canonical examples that must be representable:
#   (COMPLETE, PARTIALLY_SUFFICIENT) — execution done, evidence partial
#   (COMPLETE, INSUFFICIENT) — execution done, evidence insufficient
#   (FAILED, UNAVAILABLE) — execution failed, evidence unavailable
#   (COMPLETED_WITH_EVIDENCE_DEBT, INSUFFICIENT) — normal v1.7 completed run with queued evidence debt

CANONICAL_EXAMPLES: tuple[tuple[ExecutionStatus, EvidenceStatus], ...] = (
    (ExecutionStatus.COMPLETE, EvidenceStatus.SUFFICIENT),
    (ExecutionStatus.COMPLETE, EvidenceStatus.PARTIALLY_SUFFICIENT),
    (ExecutionStatus.COMPLETE, EvidenceStatus.INSUFFICIENT),
    (ExecutionStatus.COMPLETED_WITH_EVIDENCE_DEBT, EvidenceStatus.INSUFFICIENT),
    (ExecutionStatus.COMPLETED_WITH_EVIDENCE_DEBT, EvidenceStatus.PARTIALLY_SUFFICIENT),
    (ExecutionStatus.PARTIAL, EvidenceStatus.INSUFFICIENT),
    (ExecutionStatus.BLOCKED, EvidenceStatus.UNAVAILABLE),
    (ExecutionStatus.FAILED, EvidenceStatus.UNAVAILABLE),
)

# Mapping from legacy v1.7 RunStatus / ResolutionState to the new lattice
LEGACY_RUN_STATUS_MAP: dict[str, ExecutionStatus] = {
    "NOT_STARTED": ExecutionStatus.NOT_STARTED,
    "RUNNING": ExecutionStatus.RUNNING,
    "COMPLETED": ExecutionStatus.COMPLETE,
    "COMPLETED_WITH_EVIDENCE_DEBT": ExecutionStatus.COMPLETED_WITH_EVIDENCE_DEBT,
    "BLOCKED": ExecutionStatus.BLOCKED,
    "FAILED": ExecutionStatus.FAILED,
}

LEGACY_EVIDENCE_STATE_MAP: dict[str, EvidenceStatus] = {
    "ESTABLISHED": EvidenceStatus.SUFFICIENT,
    "PARTIALLY_ESTABLISHED": EvidenceStatus.PARTIALLY_SUFFICIENT,
    "NOT_ESTABLISHED": EvidenceStatus.INSUFFICIENT,
    "CONTRADICTED": EvidenceStatus.CONTRADICTED,
}


def combine_from_legacy(run_status: str, epistemic_state: str) -> CombinedStatus:
    execution = LEGACY_RUN_STATUS_MAP.get(run_status, ExecutionStatus.FAILED)
    evidence = LEGACY_EVIDENCE_STATE_MAP.get(epistemic_state, EvidenceStatus.INSUFFICIENT)
    return CombinedStatus(execution=execution, evidence=evidence)
