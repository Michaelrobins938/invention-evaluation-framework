---
name: conduct-patent-landscape
description: Runs a broad patent landscape search establishing filing volume, geographic distribution, top assignees, classification concentration, and filing-activity trend over time for a technology area. Use whenever the user wants a big-picture view of a patent field — "how crowded is this space," "who's filing in this area," "is this field growing." Requires a technology profile with classification candidates from analyze-technology-fundamentals as input; run that first if it doesn't exist. Do not use for assessing a specific invention's novelty against specific references — that is conduct-novelty-search.
---

# Conduct Patent Landscape

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

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
## Mandatory classification and quantitative-data gate

Before any CPC/NAICS code is used for quantitative landscape or market data:

1. Start from the classification printed on the patent front page and structured
   submission record. Never substitute a more available or higher-volume class.
2. Fetch the plain-English title for each candidate CPC/NAICS code and test thematic
   consistency against the invention description. A failed test is a hard block.
3. Record `classification-in`, `classification-verified`, and `pass/fail` in the
   avenue ledger, including the source used for the title check.
4. Narrow patent queries with invention-specific keywords in addition to the verified
   CPC code. Bare subclass totals are not invention-specific evidence.
5. Render `not established` only after a logged query was actually issued and returned
   zero, unusable, or unverifiable results. The ledger must preserve query, source,
   result count, and rejection reason. An unissued query is a pipeline defect.

## v1.7 recovery escalation

When the target has same-assignee references, continuity, or a named commercial product,
the landscape run must escalate beyond retrieval volume:

1. Reconstruct the patent family and parent/divisional/continuation relationships.
2. Review applicant/examiner citations and forward citations where available.
3. Normalize assignee variants and group publication records into families.
4. Separate retrieval volume, normalized landscape, and analytical inference in the output.
5. Follow named assignee/product/company breadcrumbs into ownership, commercialization,
   regulatory, and current-status records.

If any required path is not attempted, the proposition state is `ESCALATION_REQUIRED`,
not `SEARCH_EXHAUSTED`.
