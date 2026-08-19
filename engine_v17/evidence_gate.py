"""Schema-aware evidence admission controls for live adapter results."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any


SCHEMAS: dict[str, tuple[str, ...]] = {
    "prior_art_disclosure": (
        "patent_or_publication_id",
        "jurisdiction",
        "date",
        "relevant_passage",
        "claim_element_mapping",
    ),
    "literature_disclosure": (
        "authors",
        "title",
        "venue",
        "date",
        "doi_or_report_number",
        "url",
        "experimental_system",
        "technology",
        "application",
        "demonstrated_result",
        "relevance",
    ),
    "market_sizing": (
        "market_boundary",
        "geography",
        "time_period",
        "figure",
        "source",
        "reconciliation",
        "derivation",
    ),
    "commercial_adoption": (
        "product_identity_link",
        "source",
        "date",
    ),
    "partner_fit": (
        "organization",
        "sells",
        "buys",
        "technical_need",
        "invention_mapping",
    ),
}


class EvidenceDecision(str, Enum):
    CONFIRMED_PRESENT = "CONFIRMED PRESENT"
    WORK_QUEUE = "WORK QUEUE"
    EXCLUDED = "EXCLUDED"


@dataclass(frozen=True)
class SourceObject:
    source_identity: str
    source_type: str
    locator: str
    execution_id: str
    raw_artifact: str
    independence_lineage_id: str = ""


@dataclass(frozen=True)
class EvidenceDecisionResult:
    proposition_id: str
    schema_id: str
    state: EvidenceDecision
    source_identity: str
    errors: list[str]
    basis: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["state"] = self.state.value
        return result


def validate_schema(schema_id: str, support: dict[str, Any]) -> list[str]:
    required = SCHEMAS.get(schema_id)
    if required is None:
        return [f"unknown_schema:{schema_id}"]
    return [field for field in required if support.get(field) in (None, "", [], {})]


def apply_evidence_sufficiency_gate(
    *,
    proposition_id: str,
    schema_id: str,
    source: SourceObject,
    proposition_support: dict[str, Any] | None,
    temporal_relevance: bool,
    contradictory_evidence: bool = False,
) -> EvidenceDecisionResult:
    errors: list[str] = []
    if not source.source_identity:
        errors.append("source_identity")
    if not source.locator:
        errors.append("source_locator")
    if not source.execution_id:
        errors.append("execution_id")
    if not source.raw_artifact:
        errors.append("raw_artifact")
    if proposition_support is None:
        errors.append("direct_proposition_support")
    else:
        errors.extend(validate_schema(schema_id, proposition_support))
    if not temporal_relevance:
        errors.append("temporal_relevance")
    if contradictory_evidence:
        errors.append("contradictory_evidence")
    state = EvidenceDecision.CONFIRMED_PRESENT if not errors else EvidenceDecision.WORK_QUEUE
    basis = "Evidence Sufficiency Gate passed" if not errors else "Evidence Sufficiency Gate incomplete"
    return EvidenceDecisionResult(proposition_id, schema_id, state, source.source_identity, errors, basis)
