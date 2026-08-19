# Digest — 5-Minute Read

## Pipeline

Submission → Evidence Recovery Controller → Technology Profile → Claim Construction → Patent Landscape → Novelty Search → Literature Search → Market Opportunity → Partners → Inference Compiler → Report.

**v1.7 control layer:** unresolved evidence is classified, escalated, and constrained through the inference graph; `NOT_ESTABLISHED` requires a recovery record, and downstream conclusions inherit upstream blockers.

## Non-negotiables

0. **Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. A proposition is either admitted as an evidence-backed finding or it remains in the work queue — there is no third category.

1. **Disclosure dates are captured at intake, always** — even a confirmed "none." This is the field most likely to sink a filing if missed.
2. **Novelty ≠ FTO.** Never let a novelty search's output stand in for a freedom-to-operate opinion.
3. **Claim-construction layer.** If no formal claims exist, construct a provisional evaluation claim for analytical purposes, clearly labeled as such.
4. **Claim-element mapping is mandatory** for every reference flagged "highly relevant" or "potentially blocking." Direction: target claim limitations → reference disclosure.
5. **Hard anticipation gate.** A reference with even one missing limitation cannot be an anticipation reference. Move it to obviousness analysis.
6. **Obviousness is broader than two-reference combination.** Single-reference obvious modification is also a branch. The substitution test is one branch, not the entire definition.
7. **Relationship ontology is multi-dimensional.** E0–E5 is structural only; mechanism distance (C0–C4), design-choice distance (D0–D4), legal, and evidence layers are separate. E5 ≠ anticipation. E3 ≠ obviousness. Semantic closeness ≠ mechanism closeness. C and D are never combined into a single score.
8. **Obviousness evidence object is mandatory** whenever obviousness is assessed, backed by the **Causal Bridge Test** (prior_state → claimed_state → required_change → bridge_evidence → bridge_status). The object includes closest reference, mechanism distance (C0–C4), design-choice distance (D0–D4), knowledge decomposition, coverage, the first-class motivation object, modification paths, expectation, mechanism displacement, technical effect, unexpected result, evidence for/against, neutral signals, unresolved questions, and evidence state.
9. **Motivation is a first-class evidence object.** Categorized source lists (direct/analogous/inferred/contradicted), not counts. Status derivation is deterministic: ≥1 direct → GROUNDED; analogous only → PARTIALLY GROUNDED; inferred only → motivation not established; any contradiction → RECONCILIATION REQUIRED. A higher category never erases contradiction; analogies never accumulate into direct evidence. Ungrounded motivation → motivation not established → the obviousness proposition enters the work layer until evidence is established or avenues are exhausted.
10. **Known principle ≠ obvious application.** "Iron saturates" (confirmed principle) does not establish "a skilled engineer would choose an interposed iron-wire shield as a phase-delay mechanism" (application). The knowledge decomposition keeps `principle_known` separate from `application_known`; the application step must be evidenced independently.
11. **Unexpected-result gate.** Separate "clever" from "proven clever." If performance data is missing, flag as NOT IDENTIFIED.
12. **Three-layer epistemic architecture.** Evidence layer: CONFIRMED PRESENT / CONFIRMED ABSENT only. Work layer: NOT_STARTED (internal) / SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED (avenue-level) / EXHAUSTED (proposition-level). Analytical layer: evidence → inference → conclusion; inference is never evidence. Anti-collapse invariants: EXHAUSTED ≠ CONFIRMED ABSENT; BLOCKED ≠ CONFIRMED ABSENT; REQUIRES VERIFICATION ≠ CONFIRMED PRESENT; INFERENCE ≠ EVIDENCE; search completion is not evidence. CONFIRMED ABSENT requires a bounded evidence universe + absence_basis.
13. **Evidence Sufficiency & Search Escalation Rule.** A proposition enters the report only through the Evidence Sufficiency Gate (schema-driven, atomic). When the gate fails, the search escalates through the skill's fixed avenue checklist (deterministic priority). EXHAUSTED is a proposition-level termination state emitted only when every required avenue is COMPLETE / BLOCKED / NOT_APPLICABLE (no avenue left REQUIRES_VERIFICATION). EXHAUSTED never constitutes evidence. Unestablished propositions are omitted from factual findings and retained in the Operational Audit with barrier_type.
13. **Evidence → Inference → Conclusion firewall.** Nothing downstream promotes an inference into a fact. Every substantive finding carries proposition / evidence / inference / conclusion with strength and confidence consistent with its evidence grade. Evidence grades survive hand-offs between skills.
14. **Technical maturity ≠ commercial readiness.** Patent granted ≠ commercialization. Assignment ≠ commercialization. Technical plausibility ≠ commercialization.
15. **Decision matrix.** After claim mapping, follow the state machine: anticipation gate → obviousness analysis → motivation object → expected-success gate → causal bridge test → mechanism/design-choice distance gates → technical effect → evidence status → conclusion.
16. **Missing evidence is a work queue, not an answer.** Do not fill a gap with a plausible-sounding guess and do not report "not found" as a conclusion. Escalate the search; if avenues are exhausted, exclude the proposition from factual findings and record it in the Operational Audit. Unsourced quantitative claims are omitted.
17. **Counterfactual-exclusivity audit.** "Only partner," "no other pathway," "without X, impossible" trigger an assumption audit — replace with "strongest identified pathway"; alternatives not established (see Operational Audit).
18. **Chronology validator.** Every date and every "before [date]" is cross-checked against the filing date before delivery.
19. **Multidimensional conclusion.** No single compressed "MODERATE patentability" label and no "overall patentability" row in the default output. Per-gate table is the native output; an executive score ("Indeterminate-to-[level]") is derived only on request, labeled as a derived executive summary.
20. **Every legal-adjacent statement carries a "not legal advice" disclaimer.**
21. **Every quantitative claim is sourced**, and the final report includes a full, reproducible query log.
22. **Forward-citation counts are a neutral historical signal**, not a patentability signal. Low adoption does not establish non-obviousness.
23. **Causal Bridge Test.** The obviousness section is organized around the bridge test: what exactly must be invented between prior art and claim. bridge_status is TRAVERSED / UNTRAVERSED; when motivation or application evidence is insufficient, the bridge is not assessed as a conclusion — the proposition enters the work layer (see GLOSSARY.md). Post-filing disclosures never count as pre-filing bridge evidence.

## Where this framework stops

No claim charting beyond independent claim 1 of flagged references. No citation-network (forward/backward) analysis beyond noting it exists. No financial modeling (NPV, prosecution-cost estimate). No true FTO capability. These are intentional boundaries, not oversights — surfacing them tells a research scientist exactly where independent judgment or outside counsel is required.
