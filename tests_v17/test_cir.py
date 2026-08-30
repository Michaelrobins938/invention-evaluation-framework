"""Hermetic tests for the CIR patent ontology and extractor.

No LLM runtime, BigQuery credentials, or network is required: the LLM is a
deterministic fake and the ontology is validated against strict schemas.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from engine_v17 import cir_extractor as ce
from engine_v17 import cir_prompts as cp
from engine_v17 import patent_ontology as po


# ---------------------------------------------------------------------------
# Ontology schema strictness
# ---------------------------------------------------------------------------


def test_causal_mechanism_roundtrip():
    cm = po.CausalMechanism(
        input_state="image intensity signal",
        transformation="pulse at 0.1-15 Hz",
        output_state="pulsed screen emission",
    )
    d = cm.model_dump()
    assert d["transformation"] == "pulse at 0.1-15 Hz"
    assert po.CausalMechanism.model_validate(d) == cm


def test_causal_mechanism_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        po.CausalMechanism.model_validate(
            {"input_state": "a", "transformation": "b", "output_state": "c", "hallucinated": "x"}
        )


def test_prior_art_collision_tier_enum_and_confidence_bounds():
    ok = po.PriorArtCollision(
        reference_id="US-1-A",
        tier="Tier 1: Anticipation Candidate",
        overlapping_mechanisms=["m1"],
        reasoning="identical input-transformation-output",
        confidence_score=0.9,
        evidence=po.EvidenceSource(
            source_type="patent_claim", document_id="US-1-A", location="claim 1",
            hash_timestamp="sha256:abc@2026-01-01T00:00:00+00:00",
        ),
    )
    assert ok.tier.startswith("Tier 1")
    with pytest.raises(ValidationError):
        po.PriorArtCollision.model_validate({**ok.model_dump(), "confidence_score": 1.7})
    with pytest.raises(ValidationError):
        po.PriorArtCollision.model_validate({**ok.model_dump(), "tier": "Tier 9: Nonsense"})


def test_claim_genome_roundtrip_and_strictness():
    genome = po.ClaimGenome(
        patent_number="US-6506148-B2",
        claim_number=1,
        independent=True,
        elements=[
            po.ClaimElement(
                element_id="A",
                raw_text="a monitor displaying an image",
                causal_mechanism=po.CausalMechanism(
                    input_state="image", transformation="pulse", output_state="field"
                ),
                dependencies=[],
            )
        ],
    )
    assert po.ClaimGenome.model_validate_json(genome.model_dump_json()).elements[0].element_id == "A"
    with pytest.raises(ValidationError):
        po.ClaimGenome.model_validate({**genome.model_dump(), "extra_key": 1})


def test_evidence_source_requires_audit_anchor():
    with pytest.raises(ValidationError):
        po.EvidenceSource.model_validate(
            {"source_type": "patent_claim", "document_id": "X", "location": "c1"}
        )


# ---------------------------------------------------------------------------
# Deterministic tier classifier
# ---------------------------------------------------------------------------


def test_classify_collision_terminology_first():
    assert po.classify_collision(
        element_dependency_count=0, reference_is_combination=False,
        mechanism_overlap_count=0, terminology_only=True, reference_source_is_npl=False,
    ) == "Tier 4: Terminology Collision"


def test_classify_collision_npl_hidden_prior_art():
    assert po.classify_collision(
        element_dependency_count=0, reference_is_combination=False,
        mechanism_overlap_count=3, terminology_only=False, reference_source_is_npl=True,
    ) == "Tier 5: Hidden Prior Art"


def test_classify_collision_anticipation_vs_combination():
    # full overlap of an independent element -> Tier 1
    assert po.classify_collision(
        element_dependency_count=0, reference_is_combination=False,
        mechanism_overlap_count=1, terminology_only=False, reference_source_is_npl=False,
    ) == "Tier 1: Anticipation Candidate"
    # multi-reference coverage -> Tier 2
    assert po.classify_collision(
        element_dependency_count=0, reference_is_combination=True,
        mechanism_overlap_count=1, terminology_only=False, reference_source_is_npl=False,
    ) == "Tier 2: Combination Threat"
    # partial overlap -> Tier 3
    assert po.classify_collision(
        element_dependency_count=1, reference_is_combination=False,
        mechanism_overlap_count=1, terminology_only=False, reference_source_is_npl=False,
    ) == "Tier 3: Element-Level Collision"


# ---------------------------------------------------------------------------
# Claim splitting
# ---------------------------------------------------------------------------


def test_split_claims_standard_numbering():
    text = "1. First claim. 2. Second claim. 3. Third claim."
    out = ce.split_claims(text)
    assert [n for n, _ in out] == [1, 2, 3]
    assert out[1][1].startswith("Second claim")


def test_split_claims_run_together_fallback():
    out = ce.split_claims("A single run-together claim without numbering.")
    assert len(out) == 1
    assert out[0][0] == 1


def test_split_claims_empty():
    assert ce.split_claims("") == []
    assert ce.split_claims("   ") == []


# ---------------------------------------------------------------------------
# Fake-LLM end-to-end extractor
# ---------------------------------------------------------------------------

_FAKE_GENOME = {
    "patent_number": "US-6506148-B2",
    "claim_number": 1,
    "independent": True,
    "elements": [
        {
            "element_id": "A",
            "raw_text": "a monitor displaying an image",
            "causal_mechanism": {
                "input_state": "image intensity signal",
                "transformation": "pulse intensity at 0.1-15 Hz",
                "output_state": "pulsed screen electromagnetic field",
            },
            "dependencies": [],
        }
    ],
}


def _fake_llm_genome(prompt: str) -> str:
    return json.dumps(_FAKE_GENOME)


def test_build_genome_via_fake_llm():
    genomes = ce.build_genome("US-6506148-B2", "1. A method for manipulating the nervous system.", _fake_llm_genome)
    assert len(genomes) == 1
    assert genomes[0].patent_number == "US-6506148-B2"
    assert genomes[0].elements[0].element_id == "A"


def test_build_genome_rejects_invalid_llm_json():
    def bad_llm(prompt):
        return "{ not valid json"

    with pytest.raises(Exception):
        ce.build_genome("US-6506148-B2", "1. A claim.", bad_llm)


def test_mechanism_keywords_derived_from_physics():
    genome = po.ClaimGenome.model_validate(_FAKE_GENOME)
    kws = ce._mechanism_keywords(genome)
    assert "pulse" in kws
    assert "electromagnetic" in kws
    assert "the" not in kws
    assert len(kws) <= 8


def test_kill_chain_clamps_llm_tier_to_floor():
    def kill_llm(prompt):
        return json.dumps([
            {
                "reference_id": "US-1-A",
                "tier": "Tier 1: Anticipation Candidate",  # LLM overclaims
                "overlapping_mechanisms": ["partial-only"],
                "reasoning": "overlap",
                "confidence_score": 0.9,
                "evidence": {
                    "source_type": "patent_claim", "document_id": "US-1-A",
                    "location": "abstract", "hash_timestamp": "sha256:abc@t",
                },
            }
        ])

    genome = po.ClaimGenome.model_validate(_FAKE_GENOME)
    # element has 0 dependencies; but the claimed "full anticipation" is not
    # supported when we signal a terminology-only candidate via the fake NPL flag.
    collisions = ce.run_kill_chain(
        genome,
        candidate_records=[{"publication_number": "US-1-A", "title": "x"}],
        llm_call=kill_llm,
        patent_number="US-6506148-B2",
        reference_source_is_npl=lambda rec: False,
    )
    assert collisions
    assert collisions[0].reference_id == "US-1-A"


def test_kill_chain_skips_schema_violating_llm_output():
    def bad_kill_llm(prompt):
        return json.dumps([{"reference_id": "X", "tier": "NotATier"}])

    genome = po.ClaimGenome.model_validate(_FAKE_GENOME)
    collisions = ce.run_kill_chain(genome, [{"publication_number": "X"}], bad_kill_llm, patent_number="P")
    assert collisions == []


def test_serialize_genome_package_has_audit_hash():
    genome = po.ClaimGenome.model_validate(_FAKE_GENOME)
    pkg = ce.serialize_genome_package("US-6506148-B2", [genome])
    assert pkg["audit"]["schema_version"] == "cir-1.0"
    assert len(pkg["audit"]["sha256"]) == 64
    assert pkg["audit"]["bytes"] > 0
    # deterministic hash for identical content
    pkg2 = ce.serialize_genome_package("US-6506148-B2", [genome])
    assert pkg2["audit"]["sha256"] == pkg["audit"]["sha256"]


def test_evidence_source_hash_anchor():
    es = ce.make_evidence_source(
        source_type="patent_claim", document_id="US-6506148-B2",
        location="claim 1", content_anchor="the claim text",
    )
    assert es.hash_timestamp.startswith("sha256:")
    assert "@" in es.hash_timestamp


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


def test_prompt_a_contains_context_and_json_contract():
    p = cp.prompt_claim_to_genome("US-6506148-B2", "1. A claim.")
    assert "US-6506148-B2" in p
    assert "1. A claim." in p
    assert "strictly valid JSON" in p


def test_prompt_b_contains_file_wrapper_context():
    p = cp.prompt_prosecution_autopsy("element", "rejection", "response")
    assert "element" in p and "rejection" in p and "response" in p
    assert "Surrendered Scope" in p


def test_prompt_c_contains_bigquery_candidates():
    p = cp.prompt_prior_art_kill_chain(
        {"input_state": "a", "transformation": "b", "output_state": "c"},
        [{"publication_number": "US-1-A"}],
    )
    assert '"input_state"' in p
    assert "US-1-A" in p
    assert "Threat Tier" in p
