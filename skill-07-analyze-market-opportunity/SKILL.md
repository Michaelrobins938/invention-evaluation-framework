---
name: analyze-market-opportunity
description: Produces market sizing, industry classification, competitive landscape, SWOT, and a commercial-actionability score for an invention. Use whenever the user asks about market size, competitors, pricing, or wants a SWOT analysis. Requires the technology profile from analyze-technology-fundamentals. Do not use this for patent competitive intelligence (assignee analysis) — that's conduct-patent-landscape, though this skill should reference its output where relevant.
---

# Analyze Market Opportunity

## When to use
- "What's the market for this?" / "Who are my competitors?" / "Build a SWOT."

## When NOT to use
- The question is really about patent assignees or filing activity — use `conduct-patent-landscape`.

## Execution
1. Identify primary markets (direct, adjacent, future) with size and CAGR **from cited, defensible sources**. **A quantitative figure that cannot be reconstructed from an identified source must not appear.** If the only available evidence is qualitative (e.g., "AC infrastructure was expanding rapidly in this period"), say that — it is more useful than an impressive-looking number with no reconstructable basis. Mark any derived or estimated figure as INFERRED with its derivation shown.
2. Assign a NAICS (or regional equivalent) code.
3. Pull industry trend data — establishment count, employment, shipment value — over a multi-year window.
4. Define the opportunity structure: product/service, need, purchaser vs. end consumer, distribution channel, price point, purchase frequency.
5. **Score commercial actionability, not just size.** A technology can be technically interesting without being commercially actionable — no clear buyer, cost of production too high, regulatory pathway out of reach, or solving a problem nobody will pay to fix. Score each opportunity on: market size (low/med/high) × growth (low/med/high) × accessibility (low/med/high) × competitive intensity (low/med/high). Two or more "low" scores → flag as high-risk and say so plainly; don't soften it into a recommendation to proceed without a stated mitigating factor.
6. **Technical maturity vs. commercial readiness — separate explicitly:**
   - Patent disclosure: CONFIRMED PRESENT / NOT OBSERVED / NOT IDENTIFIED
   - Engineering feasibility: High/Med/Low (with evidence state)
   - Prototype evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED
   - Production evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED
   - Commercial adoption evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED
   - **"No evidence of adoption" is NOT OBSERVED by default**, not CONFIRMED ABSENT — historical records are rarely dense enough to establish that adoption never occurred. Use CONFIRMED ABSENT only when a **bounded evidence universe** (defined record set with documented completeness and exclusions) is specified and the record is dense enough that absence is meaningful.
   - **Coverage object on every negative finding.** Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries a coverage object: scope, temporal scope, source domains (records searched), search depth, completeness (LOW / MEDIUM / HIGH / EXHAUSTIVE), limitations. Coverage is metadata, not evidence — it never changes the evidence state; it only qualifies the reliability of the negative finding and may authorize a targeted re-evaluation. E.g., "commercial adoption of the shield mechanism in US433,700, 1890–1907, source domains: patent records + historical company records + technical literature, completeness: LOW (Westinghouse production records not reviewed)."
   - **Commercial readiness:** State "NOT EVALUATED" unless confirmed adoption evidence exists.
7. Map the competitive landscape (direct, indirect, future competitors), including each competitor's known IP posture — cross-reference `conduct-patent-landscape` output where available rather than re-deriving it.
8. Build a SWOT. Weaknesses and threats are mandatory fields, not optional ones.
9. **Counterfactual-exclusivity audit.** Audit every statement of the form "only partner," "no other pathway," "without X, impossible." Replace with "strongest identified pathway" formulations. Claiming that only one commercialization pathway exists is a claim about the absence of alternatives — which is almost never evidenced. If the record shows one strong path and others unidentified, say exactly that.

## Boundary
- Not a financial model — no NPV or breakeven calculation.
- SWOT judgments must trace back to evidence from the technology and landscape phases, not be asserted independently.
- If market data is genuinely insufficient to score actionability, say "NOT IDENTIFIED" rather than filling the gap with plausible-sounding estimates. **Never present an unsourced quantitative claim (revenue, CAGR) as a fact — omit it or mark it INFERRED with derivation.**
- Patent granted ≠ commercialization. Assignment ≠ commercialization. Technical plausibility ≠ commercialization.
