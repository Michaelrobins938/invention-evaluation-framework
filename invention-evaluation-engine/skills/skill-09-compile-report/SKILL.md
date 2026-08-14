---
name: compile-report
description: Assembles all upstream outputs (submission, technology profile, patent landscape, novelty search, literature search, market analysis, partners) into a final structured invention evaluation report with an executive summary, standard section order, appendices, and a reproducible query log. Use when the user asks for the final report, wants everything put together, or wants the deliverable prepared for a client or decision-maker. Do not use this to run new analysis — it only compiles what the other skills already produced; if a section is missing, invoke the corresponding skill first.
---

# Compile Report

## When to use
- "Generate the final report." / "Put it all together." / "Prepare the deliverable."

## When NOT to use
- Any section's underlying analysis hasn't been run yet — invoke that skill first rather than fabricating the section here.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. This skill compiles only — it never converts an unestablished proposition into a factual claim.

1. Collect all upstream outputs. If any are missing, say so and either invoke the missing skill or explicitly mark the section "NOT ESTABLISHED" in the report — never fill a gap with invented content.
2. **Run the chronology validator before writing anything.** Cross-check every date in the submission record and upstream outputs: filing date, priority date, disclosure dates, sale-offer dates, grant date, and any "before [date]" phrasing. Every "before X" must be consistent with the actual filing date. Flag and fix any mismatch (e.g., a section saying "before May 26, 1890" when the filing was March 26, 1890). This is a mandatory gate, not a style preference.
3. Write a 1–2 page executive summary **constrained to Established Findings + Analytical Conclusions** (Executive Summary ⊆ Established Findings + Analytical Conclusions). It may reference the Operational Audit ("Several evidentiary gaps remain and are documented in the Operational Audit") but never convert audit content into factual prose. Label it as a derived executive summary.
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

## Quality checklist (all must pass before delivery)
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

## Boundary
- Compiles only — generates no new analysis.
- Depth and tone match the stated audience; do not default to maximal formality if the audience is the inventor themselves.
