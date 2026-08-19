"""Patent family, status, assignment, and asset-layer controls."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RightsGraph:
    patent: str
    family: dict[str, Any] = field(default_factory=dict)
    status: dict[str, Any] = field(default_factory=dict)
    assignments: list[dict[str, Any]] = field(default_factory=list)
    asset_layers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class LegalLeverage:
    state: str
    constraints: list[str]


def build_rights_graph(records: list[dict[str, Any]]) -> RightsGraph:
    first = records[0]
    return RightsGraph(
        patent=first["patent"],
        family=dict(first.get("family", {})),
        status=dict(first.get("status", {})),
        assignments=list(first.get("assignments", [])),
        asset_layers=list(first.get("asset_layers", [])),
    )


def legal_leverage(graph: RightsGraph) -> LegalLeverage:
    if graph.status.get("active") is False or graph.status.get("state") in {"EXPIRED", "LAPSED"}:
        return LegalLeverage("minimal", ["standalone_patent_licensing_blocked", "portfolio_diligence_required"])
    return LegalLeverage("requires_verification", ["current_status_verification_required"])


def recommendation_constraints(graph: RightsGraph) -> list[str]:
    return legal_leverage(graph).constraints
