"""Dependency constraints and evidence-debt calculation."""

from dataclasses import dataclass, field
from typing import Any

from .models import Proposition, RecoveryState, ResolutionState


@dataclass
class Constraint:
    source: str
    target: str
    rule: str
    severity: str = "high"


@dataclass
class EvidenceDebtItem:
    proposition_id: str
    severity: str
    impact: list[str]
    next_action: str
    score: int


def build_dependency_graph(propositions: list[Proposition]) -> dict[str, list[str]]:
    return {p.id: list(p.downstream_effects) for p in propositions}


def propagate_constraints(propositions: list[Proposition]) -> list[Constraint]:
    constraints: list[Constraint] = []
    for p in propositions:
        if p.id.startswith("P-05") and p.search_completeness != "complete":
            constraints.extend([
                Constraint(p.id, "patentability_confidence", "anticipation_search_incomplete"),
                Constraint(p.id, "ip_leverage", "prior_art_separation_capped"),
            ])
        if p.id.startswith("P-07") and p.state != ResolutionState.ESTABLISHED:
            constraints.append(Constraint(p.id, "commercial_confidence", "market_evidence_incomplete", "moderate"))
    return constraints


def calculate_evidence_debt(propositions: list[Proposition]) -> list[EvidenceDebtItem]:
    """Evidence debt = recoverable items only.

    v1.9: a proposition is debt iff its recovery state is SEARCH_PENDING or
    ESCALATION_REQUIRED. ESTABLISHED (NONE_REQUIRED) and
    UNAVAILABLE_BY_CONSTRAINT propositions are NOT debt — the latter cannot
    be recovered by any admissible search and must not be counted as if they
    could.
    """
    items = []
    for p in propositions:
        if p.recovery_state in (RecoveryState.NONE_REQUIRED, RecoveryState.UNAVAILABLE_BY_CONSTRAINT):
            continue
        score = 100 if any(t in p.id for t in ("P-05", "P-02")) else 60
        items.append(EvidenceDebtItem(
            proposition_id=p.id,
            severity="high" if score >= 80 else "medium",
            impact=list(p.downstream_effects),
            next_action="execute recovery policy and attach exhaustion proof",
            score=score,
        ))
    return sorted(items, key=lambda item: (-item.score, item.proposition_id))


def cap_assessment(assessment: dict[str, Any], constraints: list[Constraint]) -> dict[str, Any]:
    result = dict(assessment)
    if any(c.target in {"patentability_confidence", "ip_leverage"} for c in constraints):
        result["confidence_cap"] = "low"
    if any(c.target == "commercial_confidence" for c in constraints):
        result["commercial_confidence_cap"] = "limited"
    return result
