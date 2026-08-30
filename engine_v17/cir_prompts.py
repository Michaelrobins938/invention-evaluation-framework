"""LLM extraction prompts for the Causal Intermediate Representation (CIR).

These prompts instruct the local LLM to emit the strict JSON defined in
``engine_v17/patent_ontology.py``. Every prompt closes with the same
serialisation contract: raw JSON only, no markdown fences, no commentary —
the orchestrator feeds the output directly to ``model_validate_json`` and any
schema violation is a hard failure (never coerced).

The prompts are template functions so the orchestrator can bind them to any
local LLM runtime (Ollama, llama.cpp, vLLM, an API) via an ``llm_call``
callback; the prompts themselves are runtime-agnostic.
"""

from __future__ import annotations

from typing import Any

JSON_CONTRACT = (
    "Output strictly valid JSON matching the schema. Do not include markdown "
    "formatting, code fences, or any explanation outside the JSON object. If "
    "any field is not determinable from the input, do NOT guess — mark the "
    "value as explicitly unavailable and set the confidence accordingly."
)

# ---------------------------------------------------------------------------
# Prompt A — Claim to Causal Genome
# ---------------------------------------------------------------------------


def prompt_claim_to_genome(publication_number: str, claim_text: str) -> str:
    """System directive: deconstruct one claim into its ClaimGenome JSON."""
    return f"""System Directive: You are a tier-one patent intelligence agent. Your task is
to deconstruct a patent claim into a Causal Intermediate Representation (CIR)
conforming strictly to the provided ClaimGenome JSON schema.

Input Context:
- Target Patent: {publication_number}
- Claim Text: {claim_text}

Task:
1. Decompose the claim into distinct logical elements (A, B, C...).
2. For each element, map its Causal Mechanism (Input -> Transformation ->
   Output). Do not just repeat the text; identify the underlying physical,
   chemical, or computational physics of the limitation.
3. Identify structural dependencies (e.g., if Element C requires the output
   of Element A, note it).
4. {JSON_CONTRACT}"""


# ---------------------------------------------------------------------------
# Prompt B — Prosecution Autopsy (Estoppel Extractor)
# ---------------------------------------------------------------------------


def prompt_prosecution_autopsy(
    claim_element_text: str,
    examiner_rejection_text: str,
    applicant_response_text: str,
) -> str:
    """System directive: extract ProsecutionEstoppel from the file wrapper."""
    return f"""System Directive: You are an expert patent litigator. Analyze the provided
Office Action and Applicant Response (File Wrapper) to extract Prosecution
Estoppel.

Input Context:
- Focal Claim Element: {claim_element_text}
- Office Action Excerpt: {examiner_rejection_text}
- Applicant Remarks/Amendment: {applicant_response_text}

Task:
1. Identify exactly what the applicant conceded to overcome the examiner's
   rejection.
2. Define the "Surrendered Scope" (the technological territory the patent
   owner can no longer legally claim infringement upon).
3. {JSON_CONTRACT}"""


# ---------------------------------------------------------------------------
# Prompt C — Prior Art Kill Chain Evaluator (the BigQuery bridge)
# ---------------------------------------------------------------------------


def prompt_prior_art_kill_chain(
    causal_mechanism_json: dict[str, Any],
    bq_results: list[dict[str, Any]],
) -> str:
    """System directive: tier prior-art collisions against a claim element's
    causal mechanism using BigQuery-retrieved candidates."""
    import json

    return f"""System Directive: You are an invalidity search expert. Compare a target Claim
Element's causal mechanism against a list of prior art abstracts retrieved from
BigQuery.

Input Context:
- Target Causal Mechanism: {json.dumps(causal_mechanism_json, default=str)}
- Candidate Prior Art (BigQuery Results): {json.dumps(bq_results, default=str)}

Task:
1. Ignore terminology differences. Focus purely on Structural Collision: does
   the prior art reference exhibit the identical Input -> Transformation ->
   Output?
2. If a collision exists, categorize it into a Threat Tier (1 through 5):
   Tier 1 Anticipation Candidate, Tier 2 Combination Threat, Tier 3
   Element-Level Collision, Tier 4 Terminology Collision, Tier 5 Hidden Prior
   Art.
3. Calculate a confidence score (0.0 to 1.0) based on the clarity of the
   disclosure in the prior art abstract.
4. {JSON_CONTRACT}"""
