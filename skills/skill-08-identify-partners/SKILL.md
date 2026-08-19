---
name: identify-partners
description: Compiles a prioritized list of licensing, joint-venture, or R&D-collaboration candidates with contact details and stated relevance, drawing on the competitive landscape from analyze-market-opportunity. Use whenever the user asks who to license their invention to, wants potential partners or collaborators identified, or wants to know which companies operate in their space. Do not use this for general competitor mapping without a partnership angle — that belongs in analyze-market-opportunity.
---

# Identify Partners

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- "Who should I license this to?" / "Find potential partners."

## When NOT to use
- The ask is purely about competitors, with no partnership intent — use `analyze-market-opportunity`.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. A partner-fit proposition that cannot satisfy the `partner_fit` schema escalates through the avenue checklist; if exhausted, it is excluded from factual findings and recorded in the Operational Audit.

1. Draw candidates from the `analyze-market-opportunity` competitive landscape, then expand to adjacent players not captured there — distributors, clinical partners, research collaborators.
2. For each candidate, capture the `partner_fit` schema from GLOSSARY.md: what they sell, what they buy, their technical need, and the mapping to the invention (why *this* invention would interest *this* company specifically, not a generic fit statement) — each field with source_identity. A candidate row without the sell/buy/need/mapping fields does not exist. Also capture: organization and website; contact person and role if known; proposed partnership model (licensing, JV, R&D collaboration).
3. Prioritize High/Medium/Low fit, with the reasoning stated, not just the label.
4. **Counterfactual-exclusivity audit.** Any statement that one partner is "the only" viable path, or that "without X there is no commercial vehicle," is a claim about the absence of alternatives — almost never evidenced. Reformulate as "the strongest identified pathway" and explicitly note that alternatives were not established (see Operational Audit) rather than established not to exist. Penalize exclusivity framing unless absence of alternatives is itself evidenced.

## v1.7 rights-state contract

Partner recommendations must consume the rights graph before selecting a primary
strategy. An expired or lapsed patent blocks an unqualified standalone patent-licensing
recommendation and activates portfolio, surviving-family, know-how, regulatory-asset,
clinical-data, and historical-technology diligence. Every recommendation records the
legal-status dependency and remaining evidence debt.

## Boundary
- Research output only — no outreach, and no sharing of confidential invention detail without an NDA in place.
- Contact information requires verification before use; treat it as a starting point, not a validated list.
