"""v1.9 quantitative claims registry.

Every number in a report is a first-class object with provenance:
source type, date, population, comparison group, scope, epistemic
state, and confidence. The renderer labels numbers from this registry
instead of relying on hand-written inline tags in report.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .models import EpistemicState, Scope


class SourceType(str, Enum):
    """Provenance class of a quantitative claim."""
    LLM_INFERENCE = "LLM_INFERENCE"
    INDUSTRY_BENCHMARK = "INDUSTRY_BENCHMARK"
    STRUCTURED_DATABASE = "STRUCTURED_DATABASE"
    COMPANY_REPORTED = "COMPANY_REPORTED"
    REGULATORY_RECORD = "REGULATORY_RECORD"
    PEER_REVIEWED = "PEER_REVIEWED"


@dataclass
class QuantitativeClaim:
    """One typed quantitative statement with full provenance."""
    claim_id: str
    proposition_id: str
    metric: str
    value: str                       # preserves original formatting ("~$3.25B")
    unit: str = ""
    source_type: str = SourceType.LLM_INFERENCE.value
    source: str = ""
    date: str = ""
    population: str = ""
    comparison_group: str = ""
    scope: str = Scope.TARGET_PATENT.value
    epistemic_state: str = EpistemicState.NOT_ESTABLISHED.value
    confidence: str = "LOW"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "proposition_id": self.proposition_id,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "source_type": self.source_type,
            "source": self.source,
            "date": self.date,
            "population": self.population,
            "comparison_group": self.comparison_group,
            "scope": self.scope,
            "epistemic_state": self.epistemic_state,
            "confidence": self.confidence,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuantitativeClaim":
        return cls(
            claim_id=data["claim_id"],
            proposition_id=data.get("proposition_id", ""),
            metric=data.get("metric", ""),
            value=data.get("value", ""),
            unit=data.get("unit", ""),
            source_type=data.get("source_type", SourceType.LLM_INFERENCE.value),
            source=data.get("source", ""),
            date=data.get("date", ""),
            population=data.get("population", ""),
            comparison_group=data.get("comparison_group", ""),
            scope=data.get("scope", Scope.TARGET_PATENT.value),
            epistemic_state=data.get("epistemic_state", EpistemicState.NOT_ESTABLISHED.value),
            confidence=data.get("confidence", "LOW"),
            note=data.get("note", ""),
        )


def parse_claims(raw: list[dict[str, Any]]) -> list[QuantitativeClaim]:
    """Parse a manifest ``quantitative_claims`` array.

    Raises ValueError if any claim lacks a source_type — the renderer must
    never invent provenance for a number.
    """
    claims = []
    for item in raw:
        st = item.get("source_type")
        if not st or st not in {s.value for s in SourceType}:
            raise ValueError(
                f"claim {item.get('claim_id', '?')} missing or invalid source_type")
        claims.append(QuantitativeClaim.from_dict(item))
    return claims