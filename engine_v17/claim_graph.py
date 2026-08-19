"""Claim-domain decomposition and inventive-center candidates."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClaimDomain:
    name: str
    limitations: list[str] = field(default_factory=list)


@dataclass
class ClaimVector:
    name: str
    domains: list[str]
    limitations: list[str]
    kind: str


@dataclass
class ClaimGraph:
    claim_id: str
    domains: list[ClaimDomain]
    relationships: list[tuple[str, str, str]] = field(default_factory=list)
    inventive_center_candidates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "domains": [{"name": d.name, "limitations": d.limitations} for d in self.domains],
            "relationships": [list(r) for r in self.relationships],
            "inventive_center_candidates": self.inventive_center_candidates,
        }


def decompose_claim(claim: dict[str, Any]) -> ClaimGraph:
    text = claim.get("text", "").lower()
    domains = [
        ClaimDomain("retinal_interface", ["L1"] if "electrode" in text else []),
        ClaimDomain("mechanical_fixation", ["L2"] if "strap" in text or "sclera" in text else []),
        ClaimDomain("electronics_packaging", ["L3"] if "hermetic" in text or "flip-chip" in text else []),
        ClaimDomain("interconnect", ["L4"] if "cable" in text else []),
        ClaimDomain("power_architecture", ["L5a", "L5b", "L5c", "L5d"] if "coil" in text else []),
        ClaimDomain("manufacturing_process", [],),
        ClaimDomain("surgical_handling", [],),
    ]
    domains = [d for d in domains if d.limitations or d.name in {"manufacturing_process", "surgical_handling"}]
    relationships = []
    if any(d.name == "mechanical_fixation" for d in domains) and any(d.name == "power_architecture" for d in domains):
        relationships.append(("L2", "constrains", "L5b"))
    if any(d.name == "electronics_packaging" for d in domains) and any(d.name == "power_architecture" for d in domains):
        relationships.append(("L3", "powered_by", "L5d"))
    if any(d.name == "interconnect" for d in domains) and any(d.name == "retinal_interface" for d in domains):
        relationships.append(("L4", "connects", "L1"))
    return ClaimGraph(
        claim_id=claim.get("id", "claim-unknown"),
        domains=domains,
        relationships=relationships,
        inventive_center_candidates=["cross-domain spatial integration", "low-profile scleral geometry"],
    )


def derive_claim_vectors(graph: ClaimGraph) -> list[ClaimVector]:
    product_domains = [d for d in graph.domains if d.name not in {"manufacturing_process"}]
    return [
        ClaimVector("product_architecture", [d.name for d in product_domains], [l for d in product_domains for l in d.limitations], "product"),
        ClaimVector("packaging_materials", ["electronics_packaging"], ["L3"], "product"),
        ClaimVector("manufacturing_process", ["manufacturing_process"], [], "process"),
        ClaimVector("dependent_handling", ["surgical_handling"], [], "dependent"),
    ]


def find_inventive_center(graph: ClaimGraph) -> list[str]:
    return list(graph.inventive_center_candidates)
