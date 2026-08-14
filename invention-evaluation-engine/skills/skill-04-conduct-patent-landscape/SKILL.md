---
name: conduct-patent-landscape
description: Runs a broad patent landscape search establishing filing volume, geographic distribution, top assignees, classification concentration, and filing-activity trend over time for a technology area. Use whenever the user wants a big-picture view of a patent field — "how crowded is this space," "who's filing in this area," "is this field growing." Requires a technology profile with classification candidates from analyze-technology-fundamentals as input; run that first if it doesn't exist. Do not use for assessing a specific invention's novelty against specific references — that is conduct-novelty-search.
---

# Conduct Patent Landscape

## When to use
- The user wants competitive/field-level patent context: volume, geography, assignees, trend.

## When NOT to use
- The user wants to know if their specific invention is novel or infringes — use `conduct-novelty-search` instead.

## Execution
1. Select a primary database (e.g., WIPO PatentScope) and at least one secondary source (e.g., Espacenet, Derwent) for cross-validation. Single-source landscaping systematically under-recalls — don't skip the second source.
2. Build the query from the classification candidates and core terms produced by `analyze-technology-fundamentals`.
3. **Temporal search calibration.** Determine search window based on invention date and field history, not a fixed 10–15 year window:
   - Modern fast-moving field → recent window + historical foundational art
   - Mature field → broader historical window
   - Historical invention (e.g., pre-1900) → prior-art window extending to earliest relevant technical development
   - Unknown date → establish temporal anchor first
4. For each major assignee or result cluster, note: priority date vs. filing vs. publication date; whether a patent family spans multiple jurisdictions; legal status (pending/granted/expired/abandoned — never skip this); and forward/backward citation signal where available. **For historical patents, do not import modern legal-status labels unexamined** — distinguish patent grant → historical term under applicable law → expiration, and prefer "Historical term expired: [date] (17 years from grant, subject to the historical patent regime)" over "Expired — Lifetime."
5. Extract: total family count, jurisdictional distribution, top assignees and share, CPC/IPC subclass concentration, filing trend by year.
6. Produce or describe visualizations: geographic split, assignee bar chart, time-trend line.
7. **Design-space / sibling analysis.** Identify same-inventor filings that implement the same higher-level architecture through different physical mechanisms (e.g., independent circuits vs. self-induction vs. magnetic shielding vs. core lamination). These indicate a design-space exploration event. Report the invention's position in that space — it reframes the evaluation from "is this patent novel?" to "what region of the inventor's design space does this occupy?" This is contextual evidence, not a patentability score.
8. **Negative landscape findings go through the escalation protocol.** If the landscape search returns no filings for a proposition (e.g., "no filings found in jurisdiction X"), the proposition does not become a finding. Run the skill's avenue checklist (primary source → classification search → citation expansion → terminology expansion → alternate database → organizational records → jurisdiction-specific sources → independent corroboration), logging each avenue record. Only when every required avenue is dispositioned (COMPLETE / BLOCKED / NOT_APPLICABLE) may the proposition be marked EXHAUSTED — and EXHAUSTED is not evidence: the proposition is excluded from factual findings and recorded in the Operational Audit with `barrier_type` (e.g., `insufficient_search_completion`). Single-source landscaping is one avenue, not exhaustion. CONFIRMED ABSENT additionally requires a bounded universe + absence_basis.
9. **Avenue checklist (mandatory for every negative landscape proposition).** Use the default avenue template from GLOSSARY.md (Search Escalation Protocol), customized for landscape propositions: A1 primary patent database (e.g., WIPO PatentScope), A2 classification search (CPC/IPC), A3 citation expansion, A4 terminology expansion, A5 alternate database (e.g., Espacenet, Derwent), A6 organizational records (assignee filings), A7 jurisdiction-specific sources, A8 independent corroboration. Each avenue carries an `avenue_record` with searches_run, sources_consulted, relevant_results, exclusions, limitations, completion_basis.
10. Interpret concentration signals explicitly, e.g.:
   - Academic-assignee dominance → early-stage research activity, not commercial saturation.
   - A small number of dominant assignees → consolidated field, elevated risk of blocking patents.
   - Sharp filing growth in the last 3–5 years → hot field, expect high prior-art density in the novelty search.

## Boundary
- Establishes context only — not a novelty or infringement determination.
- Result quality is bounded by query quality; refine iteratively rather than accepting a single pass.
