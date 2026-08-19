---
name: analyze-market-opportunity
description: Produces market sizing, industry classification, competitive landscape, SWOT, and a commercial-actionability score for an invention. Use whenever the user asks about market size, competitors, pricing, or wants a SWOT analysis. Requires the technology profile from analyze-technology-fundamentals. Do not use this for patent competitive intelligence (assignee analysis) — that's conduct-patent-landscape, though this skill should reference its output where relevant.
---

# Analyze Market Opportunity

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- "What's the market for this?" / "Who are my competitors?" / "Build a SWOT."

## When NOT to use
- The question is really about patent assignees or filing activity — use `conduct-patent-landscape`.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

1. Identify primary markets (direct, adjacent, future) with size and CAGR using the `market_sizing` schema from GLOSSARY.md: market boundary, geography, time period, figure, source, reconciliation, derivation. **A quantitative figure that cannot be reconstructed from an identified source must not appear** — the proposition fails the Sufficiency Gate and enters the work queue (escalate through the avenue checklist; if exhausted, record in the Operational Audit with `barrier_type: insufficient_identity` or `source_unavailable`). If the only available evidence is qualitative (e.g., "AC infrastructure was expanding rapidly in this period"), say that — it is more useful than an impressive-looking number with no reconstructable basis. Derived figures are analytical inferences, labeled as such, never evidence states.
1b. **Market relevance / demand propositions** (e.g., "government procurement activity existed for this technology") use the `market_relevance_award` or `market_relevance_report` schema: agency/publisher, award_id/report_id, recipient, date, title, URL, relevant passage, independence_lineage_id — with ≥2 independent sources. "Various SBIR awards…" with no award identities is not a finding; it is an unestablished proposition that escalates through the avenue checklist.
2. Assign a NAICS (or regional equivalent) code using the `naics_classification` schema: taxonomy_source (official NAICS/Census documentation), exact code, official title, edition year, and basis (official definition match / activity match / product-manufacturing match). **Never guess a classification.** If the official taxonomy record cannot be established, the classification proposition is excluded from factual findings and recorded in the Operational Audit with `barrier_type: insufficient_identity` — no code is reported.
3. Pull industry trend data — establishment count, employment, shipment value — over a multi-year window.
4. Define the opportunity structure: product/service, need, purchaser vs. end consumer, distribution channel, price point, purchase frequency.
5. **Score commercial actionability, not just size.** A technology can be technically interesting without being commercially actionable — no clear buyer, cost of production too high, regulatory pathway out of reach, or solving a problem nobody will pay to fix. Score each opportunity on: market size (low/med/high) × growth (low/med/high) × accessibility (low/med/high) × competitive intensity (low/med/high). Two or more "low" scores → flag as high-risk and say so plainly; don't soften it into a recommendation to proceed without a stated mitigating factor.
6. **Technical maturity vs. commercial readiness — separate explicitly:**
   - Patent disclosure: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - Engineering feasibility: High/Med/Low (with evidence state)
   - Prototype evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - Production evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - Commercial adoption evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - **Adoption is established only through the `commercial_adoption` schema**: a product-identity link (the commercial product is identifiable as embodying the claimed technology), source, date, and ≥2 independent sources (MATERIAL_PROVENANCE_INDEPENDENCE). Absence of adoption evidence is not a finding — the proposition enters the work queue; if avenues are exhausted, it is excluded from factual findings and recorded in the Operational Audit. CONFIRMED ABSENT requires a bounded evidence universe + absence_basis.
   - **Negative findings go through the escalation protocol.** Every unestablished market proposition (adoption, market relevance, market sizing) runs the skill's avenue checklist (A1 primary source search → A2 classification search → A3 citation expansion → A4 terminology expansion → A5 alternate database → A6 organizational records → A7 jurisdiction-specific sources → A8 independent corroboration), logging each avenue_record with the records actually searched (e.g., "commercial adoption of the shield mechanism in US433,700, 1890–1907, avenue records: patent records + historical company records + technical literature; Westinghouse production records BLOCKED — alternate access routes attempted"). EXHAUSTED is not evidence; the proposition is excluded from factual findings.
   - **Commercial readiness:** State "NOT ESTABLISHED" unless adoption evidence passes the Sufficiency Gate; the readiness proposition otherwise enters the work queue.
7. Map the competitive landscape (direct, indirect, future competitors), including each competitor's known IP posture — cross-reference `conduct-patent-landscape` output where available rather than re-deriving it.
8. Build a SWOT. Weaknesses and threats are mandatory fields, not optional ones.
9. **Counterfactual-exclusivity audit.** Audit every statement of the form "only partner," "no other pathway," "without X, impossible." Replace with "strongest identified pathway" formulations. Claiming that only one commercialization pathway exists is a claim about the absence of alternatives — which is almost never evidenced. If the record shows one strong path and others unidentified, say exactly that.

## Boundary
- Not a financial model — no NPV or breakeven calculation.
- SWOT judgments must trace back to evidence from the technology and landscape phases, not be asserted independently.
- If market data is genuinely insufficient to score actionability, the proposition is not established: escalate through the avenue checklist; if exhausted, exclude from factual findings and record in the Operational Audit. **Never present an unsourced quantitative claim (revenue, CAGR) as a fact — omit it or record it as an unestablished proposition.**
- Patent granted ≠ commercialization. Assignment ≠ commercialization. Technical plausibility ≠ commercialization.
## Mandatory classification and quantitative-data gate

Before any NAICS/CPC code is used for market or industry metrics:

1. Start from the classification printed on the patent front page and structured
   submission record. Never substitute a more available or higher-volume class.
2. Fetch the plain-English title for each candidate code and test thematic consistency
   against the invention description. A failed test is a hard block; reject the code.
3. Record `classification-in`, `classification-verified`, and `pass/fail` in the
   avenue ledger with the source used for the title check.
4. Pull Census establishment, employment, shipment, or revenue data only for the
   verified NAICS code. Do not publish raw classification-level totals as invention
   market data.
5. Render `not established` only after a logged query was actually issued and returned
   zero, unusable, or unverifiable results. Preserve query, source, result count, and
   rejection reason in the avenue ledger. An unissued query is a pipeline defect.

## v1.7 commercial recovery and lifecycle analysis

Do not terminate at missing TAM, revenue, reimbursement, or adoption data. Build bounded
patient-population and procedure-economics models using public proxies, and trace named
products through clinical trials, regulatory pathways, reimbursement, company history,
and market outcome. Classify unresolved commercialization history as technical,
regulatory, reimbursement, market, timing, business-model, or undetermined failure.
Then evaluate technology-resurrection paths created by changes in manufacturing, AI,
batteries, clinical practice, or regulation. Every proxy carries a decision-value label.
