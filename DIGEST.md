# Digest — 5-Minute Read

## Pipeline

Submission → Technology Profile → Claim Construction → Patent Landscape → Novelty Search → Literature Search → Market Opportunity → Partners → Report.

## Non-negotiables

1. **Disclosure dates are captured at intake, always** — even a confirmed "none." This is the field most likely to sink a filing if missed.
2. **Novelty ≠ FTO.** Never let a novelty search's output stand in for a freedom-to-operate opinion.
3. **Claim-construction layer.** If no formal claims exist, construct a provisional evaluation claim for analytical purposes, clearly labeled as such.
4. **Claim-element mapping is mandatory** for every reference flagged "highly relevant" or "potentially blocking." Direction: target claim limitations → reference disclosure.
5. **Hard anticipation gate.** A reference with even one missing limitation cannot be an anticipation reference. Move it to obviousness analysis.
6. **Obviousness is broader than two-reference combination.** Single-reference obvious modification is also a branch. The substitution test is one branch, not the entire definition.
7. **Relationship ontology is multi-dimensional.** E0–E5 is structural only; mechanism distance (C0–C4), design-choice distance (D0–D4), legal, and evidence layers are separate. E5 ≠ anticipation. E3 ≠ obviousness. Semantic closeness ≠ mechanism closeness. C and D are never combined into a single score.
8. **Obviousness evidence object is mandatory** whenever obviousness is assessed, backed by the **Causal Bridge Test** (prior_state → claimed_state → required_change → bridge_evidence → bridge_status). The object includes closest reference, mechanism distance (C0–C4), design-choice distance (D0–D4), knowledge decomposition, coverage, the first-class motivation object, modification paths, expectation, mechanism displacement, technical effect, unexpected result, evidence for/against, neutral signals, unresolved questions, and evidence state.
9. **Motivation is a first-class evidence object.** Categorized source lists (direct/analogous/inferred/contradicted), not counts. Status derivation is deterministic: ≥1 direct → GROUNDED; analogous only → PARTIALLY GROUNDED; inferred only → INFERRED; any contradiction → RECONCILIATION REQUIRED. A higher category never erases contradiction; analogies never accumulate into direct evidence. Ungrounded motivation → INFERRED → obviousness finding is UNRESOLVED.
10. **Known principle ≠ obvious application.** "Iron saturates" (confirmed principle) does not establish "a skilled engineer would choose an interposed iron-wire shield as a phase-delay mechanism" (application). The knowledge decomposition keeps `principle_known` separate from `application_known`; the application step must be evidenced independently.
11. **Unexpected-result gate.** Separate "clever" from "proven clever." If performance data is missing, flag as NOT IDENTIFIED.
12. **Evidence-state discipline.** CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED. Never convert "not identified" or "not observed" into "does not exist." **"No evidence of adoption" is NOT OBSERVED by default, not CONFIRMED ABSENT** — historical records are rarely dense enough to establish absence. CONFIRMED ABSENT additionally requires a bounded evidence universe.
13. **Negative Evidence Coverage Rule.** Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries a structured coverage object (scope, temporal scope, source domains, depth, completeness, limitations). Coverage is metadata, not evidence — it never changes evidence state, never auto-upgrades HIGH coverage to CONFIRMED ABSENT, and LOW coverage + CONFIRMED ABSENT is prohibited. You can increase search coverage without increasing certainty — you need new evidence to increase certainty.
13. **Evidence → Inference → Conclusion firewall.** Nothing downstream promotes an inference into a fact. Every substantive finding carries proposition / evidence / inference / conclusion with strength and confidence consistent with its evidence grade. Evidence grades survive hand-offs between skills.
14. **Technical maturity ≠ commercial readiness.** Patent granted ≠ commercialization. Assignment ≠ commercialization. Technical plausibility ≠ commercialization.
15. **Decision matrix.** After claim mapping, follow the state machine: anticipation gate → obviousness analysis → motivation object → expected-success gate → causal bridge test → mechanism/design-choice distance gates → technical effect → evidence status → conclusion.
16. **"Insufficient evidence" is a valid, required output.** Don't fill the gap with a plausible-sounding guess. Unsourced quantitative claims (revenue, CAGR) are omitted or marked INFERRED with derivation.
17. **Counterfactual-exclusivity audit.** "Only partner," "no other pathway," "without X, impossible" trigger an assumption audit — replace with "strongest identified pathway."
18. **Chronology validator.** Every date and every "before [date]" is cross-checked against the filing date before delivery.
19. **Multidimensional conclusion.** No single compressed "MODERATE patentability" label and no "overall patentability" row in the default output. Per-gate table is the native output; an executive score ("Indeterminate-to-[level]") is derived only on request, labeled as a derived executive summary.
20. **Every legal-adjacent statement carries a "not legal advice" disclaimer.**
21. **Every quantitative claim is sourced**, and the final report includes a full, reproducible query log.
22. **Forward-citation counts are a neutral historical signal**, not a patentability signal. Low adoption does not establish non-obviousness.
23. **Causal Bridge Test.** The obviousness section is organized around the bridge test: what exactly must be invented between prior art and claim. bridge_status is TRAVERSED / UNTRAVERSED / **UNRESOLVED** (default when motivation is INFERRED or application is NOT OBSERVED). Post-filing disclosures never count as pre-filing bridge evidence.

## Where this framework stops

No claim charting beyond independent claim 1 of flagged references. No citation-network (forward/backward) analysis beyond noting it exists. No financial modeling (NPV, prosecution-cost estimate). No true FTO capability. These are intentional boundaries, not oversights — surfacing them tells a research scientist exactly where independent judgment or outside counsel is required.
