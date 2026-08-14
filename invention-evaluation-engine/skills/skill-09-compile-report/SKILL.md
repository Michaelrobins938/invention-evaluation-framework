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
1. Collect all upstream outputs. If any are missing, say so and either invoke the missing skill or explicitly mark the section "NOT EVALUATED" in the report — never fill a gap with invented content.
2. **Run the chronology validator before writing anything.** Cross-check every date in the submission record and upstream outputs: filing date, priority date, disclosure dates, sale-offer dates, grant date, and any "before [date]" phrasing. Every "before X" must be consistent with the actual filing date. Flag and fix any mismatch (e.g., a section saying "before May 26, 1890" when the filing was March 26, 1890). This is a mandatory gate, not a style preference.
3. Write a 1–2 page executive summary: invention summary, key findings across patentability/market/risk, recommended next action.
4. Assemble the body in standard order: Executive Summary → Technology Analysis → Landscape Analysis → IP/Novelty Analysis → Market Analysis → Opportunity Assessment → Potential Partners → Appendices.
5. Include all tables and figures generated upstream rather than re-summarizing them in prose.
6. **Mandatory: Evidence Audit appendix.** For every key claim (anticipation, obviousness, market size, etc.), state the evidence status (CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED) and the source searched. **Every negative finding (NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT) must carry its coverage object** — scope, temporal scope, source domains, search depth, completeness, limitations — and CONFIRMED ABSENT must cite its bounded evidence universe. This is how you show your work.
7. **Mandatory: Insufficient Evidence / Not Evaluated section.** List everything flagged as NOT IDENTIFIED, NOT OBSERVED, or NOT EVALUATED in upstream skills — do not bury these in appendices; surface them in the main report.
8. **Mandatory: Decision Matrix output.** Include the state machine result from Skill 05, showing the path taken (anticipation gate → obviousness analysis → motivation object → expected-success gate → causal bridge test → mechanism/design-choice distance gates → technical effect → evidence status → conclusion). For obviousness, include the Causal Bridge Test (with bridge_status) and the structured obviousness evidence object.
9. **Mandatory: Multidimensional conclusion.** Do not collapse the result into a single "MODERATE patentability" label. Output the per-gate table (utility / novelty / causal distinction with C0–C4 / D0–D4 / obviousness risk / causal bridge status / unexpected-result / disclosure coverage / adoption evidence / market sizing). **There is no "Overall patentability" row in the default conclusion.** An executive score ("Indeterminate-to-[level]") is derived **only if the user explicitly requests an executive summary score**; when derived, label it as a derived executive summary (not a pipeline output) and always accompany it with the full per-gate table.
10. **Evidence firewall at compile time.** Every proposition carried into the report must keep the evidence grade it was established with. An INFERRED or NOT OBSERVED proposition may not be silently upgraded to CONFIRMED ABSENT or CONFIRMED PRESENT in the report. If a section's conclusion is stronger than its evidence grade, downgrade the conclusion.
11. **Historical patent-status normalization.** For historical patents, use "Historical term expired: [date] (17 years from grant, subject to the historical patent regime)" rather than modern labels like "Expired — Lifetime."
12. **Forward-citation labeling.** Low forward-citation counts are a neutral historical technology-development signal, not a patentability signal. Do not present them as evidence for or against obviousness.
13. Add appendices: patentability primer, search methodology, **full query log** (every query string run, per skill, with database and date), original submission record.
14. Run the quality checklist below before delivery.
15. Deliver in the requested format, matched in tone and depth to the audience (inventor vs. TTO vs. investor vs. outside counsel).

## Quality checklist (all must pass before delivery)
- [ ] Every quantitative claim is sourced — or omitted / marked INFERRED with derivation. No unsourced revenue or CAGR figures.
- [ ] Chronology validator passed: all dates consistent, no "before [wrong date]" phrasing.
- [ ] Every legal-adjacent statement (patentability, FTO-adjacent, regulatory) carries a "not legal advice" disclaimer.
- [ ] The novelty section explicitly states it is not an FTO opinion if any FTO-adjacent question was raised anywhere in the engagement.
- [ ] The query log is complete enough that a reviewer could re-run any search and reproduce the result set.
- [ ] Any "NOT IDENTIFIED", "NOT OBSERVED", or "NOT EVALUATED" flags from upstream skills are carried into the report rather than silently dropped.
- [ ] Evidence Audit appendix is present and maps each key finding to its evidence status.
- [ ] Commercial readiness is stated as "NOT EVALUATED" unless confirmed adoption evidence exists; "no evidence of adoption" is labeled NOT OBSERVED, not CONFIRMED ABSENT, unless coverage is demonstrably sufficient.
- [ ] Decision matrix output is included, showing the reasoning path, and if obviousness was assessed, the Causal Bridge Test (with bridge_status) and the structured obviousness evidence object are provided.
- [ ] Conclusion is multidimensional (per-gate table), not a single compressed patentability label; **no scalar "overall patentability" label appears in the default conclusion output** (an executive score appears only if explicitly requested, labeled as a derived executive summary).
- [ ] Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries its coverage object; CONFIRMED ABSENT cites a bounded evidence universe.
- [ ] No exclusivity framing ("only partner," "no other pathway") survives without an assumption audit.
- [ ] Claim-construction layer (if used) is clearly labeled as "provisional evaluation claim — not a legal claim construction."

## Boundary
- Compiles only — generates no new analysis.
- Depth and tone match the stated audience; do not default to maximal formality if the audience is the inventor themselves.
