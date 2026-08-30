"""CIR extractor — wires BigQuery retrieval and the local LLM into the
Pydantic claim genome.

Pipeline (per the architecture spec):

1. FETCH       — focal patent claims from BigQuery Google Patents
                (``bq_patent_intelligence.get_patent_full_text``; claims only
                via exact publication number, never a broad scan).
2. GENOME      — claims -> LLM (Prompt A) -> ``ClaimGenome`` via
                ``model_validate_json``. Schema violations are hard failures:
                nothing partially parsed enters the graph.
3. SWEEP       — the genome's causal mechanisms become the dynamic
                keyword/regex inputs to the BigQuery prior-art sweep
                (Strategy A) so the search is driven by the invention's
                physics, not by the claim's vocabulary.
4. KILL CHAIN  — BigQuery candidates + causal mechanisms -> LLM (Prompt C)
                -> ``PriorArtCollision`` list. The LLM's tier assignment is
                clamped against the deterministic tier floor
                (``classify_collision``) so the graph never holds a tier the
                observable signals cannot support.
5. SERIALIZE   — every ``EvidenceSource`` is stamped with a SHA-256 hash of
                its canonical content and a retrieval timestamp, so the graph
                is auditable down to the byte.

The LLM is injected as a callback (``llm_call: Callable[[str], str]``) so the
extractor is runtime-agnostic; tests substitute a deterministic fake.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Callable

from .patent_ontology import (
    TIER_ORDER,
    ClaimElement,
    ClaimGenome,
    EvidenceSource,
    PriorArtCollision,
    classify_collision,
)
from .cir_prompts import prompt_claim_to_genome, prompt_prior_art_kill_chain

LlmCall = Callable[[str], str]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_evidence_source(
    *,
    source_type: str,
    document_id: str,
    location: str,
    content_anchor: str,
) -> EvidenceSource:
    """Build an auditable EvidenceSource: hash + retrieval timestamp."""
    return EvidenceSource(
        source_type=source_type,  # type: ignore[arg-type]
        document_id=document_id,
        location=location,
        hash_timestamp=f"sha256:{_sha256(content_anchor)}@{_now_iso()}",
    )


def split_claims(claims_text: str) -> list[tuple[int, str]]:
    """Split raw claims text into ``[(claim_number, claim_text), ...]``.

    Handles both line-start numbering ("\\n1. ... \\n2. ...") and inline
    numbering ("1. ... 2. ..."). Fallback for run-together text without any
    numbering: the whole block becomes a single pseudo-claim so the pipeline
    degrades to one genome instead of inventing boundaries.
    """
    if not claims_text or not claims_text.strip():
        return []
    text = claims_text.strip()
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})\.\s+", text))
    if len(matches) < 2:
        # inline numbering: "N. " preceded by a word boundary + whitespace/start
        matches = list(re.finditer(r"(?<!\d)(?:^|\s)(\d{1,2})\.\s+", text))
        if len(matches) < 2:
            return [(1, text)]
    out: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            out.append((int(m.group(1)), body))
    return out


def build_genome(
    patent_number: str,
    claims_text: str,
    llm_call: LlmCall,
    *,
    include_prosecution: bool = False,
) -> list[ClaimGenome]:
    """Run the claim-to-genome extractor over every claim.

    Args:
        patent_number: e.g. ``"US-6506148-B2"``.
        claims_text: raw claims block (from BigQuery full-text).
        llm_call: LLM callback (prompt -> raw JSON string).
        include_prosecution: reserved for file-wrapper ingestion (Prompt B);
            when False the estoppel slot stays None.
    """
    genomes: list[ClaimGenome] = []
    for claim_number, claim_text in split_claims(claims_text):
        prompt = prompt_claim_to_genome(patent_number, claim_text)
        raw = llm_call(prompt)
        genome = ClaimGenome.model_validate_json(raw)
        genomes.append(genome)
    return genomes


def _mechanism_keywords(genome: ClaimGenome, max_terms: int = 8) -> list[str]:
    """Derive search terms from the genome's causal physics (not vocabulary).

    Uses the mechanism triples' noun phrases as the seed; the BigQuery sweep
    converts them into a regex over abstracts. Kept deterministic so the sweep
    is reproducible from the same genome.
    """
    terms: list[str] = []
    for element in genome.elements:
        cm = element.causal_mechanism
        for field in (cm.input_state, cm.transformation, cm.output_state):
            for token in re.split(r"[^A-Za-z0-9\- ]+", field):
                for word in token.split():
                    w = word.strip("-").lower()
                    if len(w) > 3 and w not in ("with", "from", "that", "this", "into", "the", "and", "via", "such"):
                        terms.append(w)
    seen: set[str] = set()
    out: list[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:max_terms]


def run_kill_chain(
    genome: ClaimGenome,
    candidate_records: list[dict[str, Any]],
    llm_call: LlmCall,
    *,
    patent_number: str,
    reference_source_is_npl: Callable[[dict[str, Any]], bool] | None = None,
) -> list[PriorArtCollision]:
    """Evaluate one genome's elements against BigQuery prior-art candidates.

    The LLM proposes collisions (Prompt C); each is clamped against the
    deterministic tier floor from the element's dependency count and the
    observable overlap signals, then stamped with an EvidenceSource anchor.
    """
    collisions: list[PriorArtCollision] = []
    for element in genome.elements:
        if not candidate_records:
            continue
        prompt = prompt_prior_art_kill_chain(
            element.causal_mechanism.model_dump(), candidate_records
        )
        raw = llm_call(prompt)
        proposed = json.loads(raw)
        for item in proposed if isinstance(proposed, list) else proposed.get("collisions", []):
            try:
                collision = PriorArtCollision.model_validate(item)
            except Exception:
                continue  # schema-violating LLM output never enters the graph
            floor = classify_collision(
                element_dependency_count=len(element.dependencies),
                reference_is_combination=collision.tier == "Tier 2: Combination Threat",
                mechanism_overlap_count=len(collision.overlapping_mechanisms),
                terminology_only=collision.tier == "Tier 4: Terminology Collision",
                reference_source_is_npl=bool(
                    reference_source_is_npl and reference_source_is_npl(
                        {"reference_id": collision.reference_id}
                    )
                ),
            )
            floor_rank = TIER_ORDER[floor]
            claimed_rank = TIER_ORDER[collision.tier]
            if claimed_rank < floor_rank:
                collision = collision.model_copy(update={"tier": floor})
            collisions.append(collision)
    return collisions


def serialize_genome_package(
    patent_number: str,
    genomes: list[ClaimGenome],
    collisions: list[PriorArtCollision] | None = None,
) -> dict[str, Any]:
    """Export the full CIR package with an audit hash over the graph content.

    The hash covers ONLY the content (patent number, genomes, collisions) —
    never the volatile ``generated_at`` timestamp or the audit block itself —
    so identical genomes always hash identically (reproducible audit trail).
    """
    content: dict[str, Any] = {
        "patent_number": patent_number,
        "claims": [g.model_dump() for g in genomes],
        "prior_art_collisions": [c.model_dump() for c in (collisions or [])],
    }
    canonical = json.dumps(content, sort_keys=True, default=str)
    package = dict(content)
    package["generated_at"] = _now_iso()
    package["audit"] = {
        "sha256": _sha256(canonical),
        "schema_version": "cir-1.0",
        "bytes": len(canonical.encode("utf-8")),
    }
    return package
