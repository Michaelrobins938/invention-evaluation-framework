"""Pydantic ontology for the Causal Intermediate Representation (CIR).

This is the strict, versioned JSON contract that the local LLM must emit when
deconstructing a patent claim into its causal genome. It is the interface
between *document retrieval* (BigQuery Google Patents, file wrappers, NPL) and
*decision architecture* (the evidence graph).

Design invariants:

- Every piece of evidence carries an auditable ``EvidenceSource`` with a
  document id, an in-document location, and a SHA-256 hash or retrieval
  timestamp so the graph can be verified down to the byte.
- A ``ClaimElement`` is not a text snippet; it is a ``CausalMechanism``
  (input → transformation → output) plus dependency edges, so prior-art
  collisions are detected by structural (causal-chain) identity rather than
  keyword overlap.
- ``PriorArtCollision`` tiers follow the kill-chain severity ladder:
    Tier 1 — anticipation candidate
    Tier 2 — combination threat
    Tier 3 — element-level collision
    Tier 4 — terminology collision
    Tier 5 — hidden prior art
- ``ProsecutionEstoppel`` captures the negative space the applicant
  surrendered during examination (the "shadow architecture"), so any
  evidence-of-use that relies on surrendered territory is flagged as
  high-enforceability-risk downstream.

Validation is strict (Literal enums, bounded confidence, required fields).
Any LLM output that does not satisfy the schema fails ``model_validate_json``
and is refused entry to the graph — no partial or silent coercion.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSource(BaseModel):
    """Where a factual proposition comes from, with an audit anchor."""

    source_type: Literal["patent_claim", "scientific_paper", "prosecution_history", "product_doc"]
    document_id: str
    location: str = Field(description="Paragraph, claim number, or page line")
    hash_timestamp: str = Field(
        description="SHA-256 hash or retrieval timestamp for auditability"
    )

    model_config = ConfigDict(extra="forbid")


class CausalMechanism(BaseModel):
    """The physical/computational chain of a claim element.

    Collision detection operates on this triple, not on surface wording.
    """

    input_state: str = Field(description="What is received, measured, or acquired")
    transformation: str = Field(description="The physical or computational state change")
    output_state: str = Field(
        description="The resulting action, control signal, or physical product"
    )

    model_config = ConfigDict(extra="forbid")


class ProsecutionEstoppel(BaseModel):
    """What the applicant explicitly gave up during examination."""

    original_text: str
    rejection_basis: Literal["101", "102", "103", "112"]
    cited_art: list[str]
    surrendered_scope: str = Field(
        description="What specific interpretation the applicant explicitly gave up"
    )
    evidence: EvidenceSource

    model_config = ConfigDict(extra="forbid")


class PriorArtCollision(BaseModel):
    """A structural collision between a claim element and prior art."""

    reference_id: str
    tier: Literal[
        "Tier 1: Anticipation Candidate",
        "Tier 2: Combination Threat",
        "Tier 3: Element-Level Collision",
        "Tier 4: Terminology Collision",
        "Tier 5: Hidden Prior Art",
    ]
    overlapping_mechanisms: list[str]
    reasoning: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    evidence: EvidenceSource

    model_config = ConfigDict(extra="forbid")


class ClaimElement(BaseModel):
    """One atomic element of a claim, in CIR form."""

    element_id: str
    raw_text: str
    causal_mechanism: CausalMechanism
    dependencies: list[str] = Field(
        description="List of element_ids this element depends on"
    )
    prosecution_estoppel: Optional[ProsecutionEstoppel] = None
    prior_art_collisions: list[PriorArtCollision] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class ClaimGenome(BaseModel):
    """The complete causal genome of one claim."""

    patent_number: str
    claim_number: int
    independent: bool
    elements: list[ClaimElement]

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Deterministic tier classification (used by the kill-chain evaluator before
# the LLM is consulted, and as a floor under the LLM's tier assignment).
# ---------------------------------------------------------------------------

TIER_ORDER = {
    "Tier 1: Anticipation Candidate": 1,
    "Tier 2: Combination Threat": 2,
    "Tier 3: Element-Level Collision": 3,
    "Tier 4: Terminology Collision": 4,
    "Tier 5: Hidden Prior Art": 5,
}


def classify_collision(
    *,
    element_dependency_count: int,
    reference_is_combination: bool,
    mechanism_overlap_count: int,
    terminology_only: bool,
    reference_source_is_npl: bool,
) -> str:
    """Deterministic tier floor from observable signals.

    Used by the CIR extractor to sanity-check (and clamp) the LLM's tier
    assignment. Ordering: a single-reference collision that covers every
    mechanism of an independent element is an anticipation candidate (Tier 1);
    multi-reference coverage is a combination threat (Tier 2); partial
    mechanism overlap is element-level (Tier 3); pure wording overlap without
    causal overlap is terminology (Tier 4); collisions surfaced only from
    non-patent literature are hidden prior art (Tier 5).
    """
    if terminology_only:
        return "Tier 4: Terminology Collision"
    if reference_source_is_npl:
        return "Tier 5: Hidden Prior Art"
    if reference_is_combination:
        return "Tier 2: Combination Threat"
    if mechanism_overlap_count >= max(1, element_dependency_count + 1):
        return "Tier 1: Anticipation Candidate"
    if mechanism_overlap_count >= 1:
        return "Tier 3: Element-Level Collision"
    return "Tier 4: Terminology Collision"
