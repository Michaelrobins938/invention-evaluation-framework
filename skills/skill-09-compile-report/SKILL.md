---
name: compile-report
description: Assembles all upstream outputs (submission, technology profile, patent landscape, novelty search, literature search, market analysis, partners) into a final structured invention evaluation report with an executive summary, standard section order, appendices, and a reproducible query log. Use when the user asks for the final report, wants everything put together, or wants the deliverable prepared for a client or decision-maker. Do not use this to run new analysis — it only compiles what the other skills already produced; if a section is missing, invoke the corresponding skill first.
---

# Compile Report

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- "Generate the final report." / "Put it all together." / "Prepare the deliverable."

## When NOT to use
- Any section's underlying analysis hasn't been run yet — invoke that skill first rather than fabricating the section here.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. This skill compiles only — it never converts an unestablished proposition into a factual claim.

1. Collect all upstream outputs. If any are missing, say so and either invoke the missing skill or explicitly mark the section "NOT ESTABLISHED" in the report — never fill a gap with invented content.
1a. **Write the compiled Markdown to the resolved run directory before delivery.**
    The report compiler must receive an absolute output path from the engine
    artifact-destination gate. If no path is supplied, compilation is blocked;
    do not return an unsaved report as if it were a deliverable.
2. **Run the chronology validator before writing anything.** Cross-check every date in the submission record and upstream outputs: filing date, priority date, disclosure dates, sale-offer dates, grant date, and any "before [date]" phrasing. Every "before X" must be consistent with the actual filing date. Flag and fix any mismatch (e.g., a section saying "before May 26, 1890" when the filing was March 26, 1890). This is a mandatory gate, not a style preference.
3. Write a 1–2 page executive summary **constrained to Established Findings + Analytical Conclusions** (Executive Summary ⊆ Established Findings + Analytical Conclusions). It may reference the Operational Audit ("Several evidentiary gaps remain and are documented in the Operational Audit") but never convert audit content into factual prose. Label it as a derived executive summary.
3a. **Executive-summary substructure is prescribed — do not improvise section names or contents.** Use exactly:
   - **1.1 Evaluation Overview** — gauge/graphic plus metadata; every pointer the graphic makes ("evidence documented in…") must resolve to a section that actually contains that content.
   - **1.2 Bottom Line** — the recommendation and its confidence.
   - **1.3 Rating Methodology** — mandatory contents: (a) the rating scale, (b) per-component scoring criteria, (c) component weights, (d) score→rating thresholds, (e) a worked example showing how totals map to labels. If two dimensions show identical raw points but different ratings, the differing weights must be stated explicitly — never leave the reader to reverse-engineer the mapping.
   - **1.4 Key Evidence Supporting the Ratings** — plain-language established findings (with proposition_id and source) backing each rating.
   Unresolved propositions NEVER appear inside sections 1.x or between them. Evidence gaps, debt tables, and barrier classifications belong exclusively in the appendix "Evidence Gaps and Audit Manifest."
3b. **Proposition Identifier Legend is mandatory** (appendix or end of executive summary). Explain the numbering scheme at first use: `P-<phase>-<seq>` propositions (phase numbers match pipeline phases), letter suffixes (`P-05-008a`) for derived sub-propositions, `A-*` avenue records, `R<n>` reviewed references, `C<n>` claim groupings, `C0–C4` mechanism distance, `D0–D4` design-choice distance. This is internal audit vocabulary — the legend makes it navigable, but client-facing prose must lead with plain language and use IDs as references, not as the primary vocabulary.
3c. **Proposition IDs are globally unique across the entire report.** One ID maps to exactly one subject. Reusing an ID for two subjects (e.g., market sizing and a landscape statistics item both called `P-07-001`) is a compilation failure — assign a fresh ID and cross-reference instead.
3d. **Audit-table columns are fixed:** `| Proposition ID | Work state | Barrier type | Description |`. Barrier type carries only enum values (`source_unavailable`, `insufficient_identity`, `insufficient_search_completion`, `insufficient_corroboration`, `insufficient_temporal_match`, `unresolved_conflict`, `scope_mismatch`, `insufficient_technical_demonstration`). Free-text descriptions belong in the Description column — never in the Barrier type column.
3e. **No template residue may reach delivery.** Any unfilled placeholder (`[RELEVANT POC WILL BE LINKED HERE]`, `[TODO…]`) fails the report. Scan before delivering; remove or fill every bracketed placeholder.
3f. **Source-identity hygiene.** A source identity names an external database/publisher/document with a locator (e.g., "EPO OPS, publication US8527057B2 biblio"). Internal process descriptions ("Verification rounds 1–5", "internal review pass 2") are not sources and must never appear in a source column or citation list.
3g. **Market-definition reconciliation is shown, not asserted.** When figures combine different market definitions (e.g., ART services vs ART products vs IVF cycles), include an explicit reconciliation table: definition | figure | source | how it was combined or why it cannot be. Writing "reconciled" without the table is prohibited.
3h. **Geographic presentation uses comparable categories.** Do not mix rows of different kinds (countries, political/economic blocs, national programs) in one table as if commensurable — separate them or state the basis on which they are compared.
3i. **Bounded emptiness language.** Claims like "the niche is empty" overreach the evidence. Required form: "no filings were identified within the bounded search universe (databases X, Y; date range; classification Z)". State the boundary wherever absence is claimed.
3j. **Formal-conclusion language discipline.** Terms like "NOT ANTICIPATED" carry legal weight; use them only inside clearly-labeled preliminary analytical context, each occurrence within reach of the not-legal-advice disclaimer. FTO-adjacent phrasing triggers the explicit "this is not an FTO opinion" statement in the same section.
4. Assemble the body in standard order: Executive Summary → Technology Analysis → Landscape Analysis → IP/Novelty Analysis → Market Analysis → Opportunity Assessment → Potential Partners → Appendices.
5. Include all tables and figures generated upstream rather than re-summarizing them in prose.
6. **Mandatory: Established Findings section.** Only rows that passed the Evidence Sufficiency Gate (CONFIRMED PRESENT / CONFIRMED ABSENT), each rendered from its finding object with full provenance (proposition_id, source_identity, locator, absence_basis where applicable).
7. **Mandatory: Analytical Conclusions section.** Per-gate results whose premises are established findings, each with a premise map (conclusion_id, gate, premises: [proposition_ids], inference: statement + rule_applied, conclusion: assessment). No orphan conclusions; no premise whose status is a work state. **UNRESOLVED may not appear as a terminal analytical conclusion.** Three outcomes only: more work → work layer; all work exhausted → exclude proposition; supported evidence → analytical conclusion permitted.
8. **Mandatory: Operational Audit section.** Every unestablished proposition: proposition_id, work state, avenue dispositions (COMPLETE / BLOCKED / NOT_APPLICABLE + rule_id), barrier_type, remaining_evidentiary_barrier. The reproducible query log = the full escalation ladder (all avenue records, in priority order). **Allowed language:** "Commercial adoption could not be established from the completed evidence protocol." **Prohibited language** (and semantic equivalents) in factual findings: "Not found," "No X was identified," "No evidence of X exists," "appears absent," "there is no evidence that…," "apparently none," "likely not," "could not locate," "no known," "none identified," "no record was found," "Inferred," "Medium completeness."
9. **Mandatory: Decision Matrix output.** Include the state machine result from Skill 05, showing the path taken (anticipation gate → obviousness analysis → motivation object → expected-success gate → causal bridge test → mechanism/design-choice distance gates → technical effect → evidence sufficiency gate → finding or work queue). For obviousness, include the Causal Bridge Test (with bridge_status TRAVERSED / UNTRAVERSED) and the structured obviousness evidence object.
10. **Historical patent-status normalization.** For historical patents, use "Historical term expired: [date] (17 years from grant, subject to the historical patent regime)" rather than modern labels like "Expired — Lifetime."
11. **Forward-citation labeling.** Low forward-citation counts are a neutral historical technology-development signal, not a patentability signal. Do not present them as evidence for or against obviousness.
12. Add appendices: patentability primer, search methodology, **full query log** (every avenue record, per skill, with database and date), original submission record.
13. Run the quality checklist below before delivery.
14. Deliver in the requested format, matched in tone and depth to the audience (inventor vs. TTO vs. investor vs. outside counsel).
15. Return a delivery manifest containing the absolute paths of the compiled
    report, submission record, proposition ledger, avenue ledger, scores manifest,
    and rendered HTML/PDF. Verify each path exists and has non-zero size.

## Quality checklist (all must pass before delivery)
- [ ] Executive-summary substructure is exactly 1.1 Evaluation Overview / 1.2 Bottom Line / 1.3 Rating Methodology / 1.4 Key Evidence Supporting the Ratings — no improvised section names.
- [ ] Every pointer made by the 1.1 graphic resolves to a section that actually contains the promised content.
- [ ] 1.3 discloses scale, criteria, weights, and thresholds; identical totals under equal weights received identical ratings; any divergence is explained by stated weights.
- [ ] Unresolved propositions appear ONLY in the Evidence Gaps and Audit Manifest appendix — never in sections 1.x or between them.
- [ ] Proposition Identifier Legend present; every proposition ID unique across the whole report (no ID bound to two subjects).
- [ ] Audit tables use fixed columns with enum barrier types only; descriptions in the Description column.
- [ ] No template placeholders (`[ALL-CAPS …]`) anywhere in the deliverable — scanned, not assumed.
- [ ] Every source identity is an external database/publisher/document with locator; no internal process labels cited as sources.
- [ ] Combined market figures carry a reconciliation table; geographic tables compare like categories only.
- [ ] Absence claims state their bounded search universe; no unbounded emptiness language ("the niche is empty").
- [ ] Every quantitative claim is sourced — or the proposition is excluded from factual findings and recorded in the Operational Audit. No unsourced revenue or CAGR figures.
- [ ] Chronology validator passed: all dates consistent, no "before [wrong date]" phrasing.
- [ ] Every legal-adjacent statement (patentability, FTO-adjacent, regulatory) carries a "not legal advice" disclaimer.
- [ ] The novelty section explicitly states it is not an FTO opinion if any FTO-adjacent question was raised anywhere in the engagement.
- [ ] The query log (avenue records) is complete enough that a reviewer could re-run any search and reproduce the result set.
- [ ] Every unestablished proposition from upstream skills is carried into the Operational Audit rather than silently dropped.
- [ ] Established Findings contains only CONFIRMED PRESENT / CONFIRMED ABSENT rows, each with full provenance; CONFIRMED ABSENT rows carry absence_basis.
- [ ] Every Analytical Conclusion carries a premise map whose premises are established findings; no premise is a work state.
- [ ] No legacy evidence states (NOT OBSERVED / NOT IDENTIFIED / INFERRED / NOT EVALUATED / CONTESTED / UNRESOLVED) appear as active semantics anywhere in the report.
- [ ] No prohibited negative language ("not found," "no evidence of X exists," "none identified," etc.) appears outside the Operational Audit.
- [ ] Commercial readiness is stated as "NOT ESTABLISHED" unless adoption evidence passes the Sufficiency Gate.
- [ ] Decision matrix output is included, showing the reasoning path, and if obviousness was assessed, the Causal Bridge Test (with bridge_status TRAVERSED/UNTRAVERSED) and the structured obviousness evidence object are provided.
- [ ] Conclusion is multidimensional (per-gate table), not a single compressed patentability label; **no scalar "overall patentability" label appears in the default conclusion output** (an executive score appears only if explicitly requested, labeled as a derived executive summary).
- [ ] Executive Summary ⊆ Established Findings + Analytical Conclusions.
- [ ] No exclusivity framing ("only partner," "no other pathway") survives without an assumption audit.
- [ ] Claim-construction layer (if used) is clearly labeled as "provisional evaluation claim — not a legal claim construction."

## v1.7 graph compilation contract

Compile conclusions from evidence-graph artifacts, not from free-form section text.
Every score and recommendation must expose confidence, basis proposition IDs, blockers,
evidence debt, and next recovery action. The compiler must propagate upstream constraints
and must not upgrade `ESCALATION_REQUIRED`, `BLOCKED`, or `UNRESOLVED — SEARCH-INCOMPLETE`
into a positive conclusion.

## Boundary
- Compiles only — generates no new analysis.
- Depth and tone match the stated audience; do not default to maximal formality if the audience is the inventor themselves.
