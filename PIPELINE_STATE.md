# Pipeline State — Invention Evaluation Framework

**Version:** v1.6 (Evidence Sufficiency Architecture — three-layer epistemic model, Sufficiency Gate, Search Escalation Protocol, Proposition-Schema Registry, Operational Audit)
**Status:** v1.6 implemented; end-to-end validation on Tesla US433,700 in progress (see Test-report-results/).
**Supersedes:** v1.5 (Causal Bridge Test, mechanism/design-choice distance, Negative Evidence Coverage Rule, first-class Motivation Object, per-gate-only conclusion) — validation record retained below.

## Skill status

| # | Skill | SKILL.md | Under 500 lines | Frontmatter (name+description only) |
|---|---|---|---|---|
| 01 | invention-evaluation-overview | ✅ | ✅ | ✅ |
| 02 | gather-invention-submission | ✅ | ✅ | ✅ |
| 03 | analyze-technology-fundamentals | ✅ | ✅ | ✅ |
| 04 | conduct-patent-landscape | ✅ | ✅ | ✅ |
| 05 | conduct-novelty-search | ✅ | ✅ | ✅ |
| 06 | conduct-literature-search | ✅ | ✅ | ✅ |
| 07 | analyze-market-opportunity | ✅ | ✅ | ✅ |
| 08 | identify-partners | ✅ | ✅ | ✅ |
| 09 | compile-report | ✅ | ✅ | ✅ |

## v1.4 changes

| Area | Change |
|---|---|
| Evidence ontology | Expanded to 7 states: CONFIRMED PRESENT / CONFIRMED ABSENT / **NOT OBSERVED** / NOT IDENTIFIED / NOT EVALUATED / **INFERRED** / **CONTESTED**. NOT OBSERVED is the default for negative historical claims (coverage-insufficient); CONFIRMED ABSENT requires coverage-sufficient records. |
| Evidence → Inference → Conclusion firewall | Formalized finding structure (proposition / evidence / inference / conclusion with strength + confidence). Nothing downstream promotes an inference into a fact; evidence grades survive skill hand-offs. |
| Obviousness gates | Motivation gate (evidence-grounded, else INFERRED → UNRESOLVED), expected-success gate, causal-distance gate. Known principle ≠ obvious application. |
| New metrics | Mechanism displacement (where the causal intervention point moved) and causal distance (C0–C4), distinct from structural E0–E5. |
| Combination novelty | Renamed **combination-obviousness exposure** (derivation risk) — a combination can be novel yet obvious. |
| Forward citations | Relabeled as neutral historical signals, not patentability evidence. |
| Market skill | Unsourced quantitative claims (revenue, CAGR) prohibited or marked INFERRED; adoption absence defaults to NOT OBSERVED; counterfactual-exclusivity audit added. |
| Partners skill | Counterfactual-exclusivity audit: "only partner" → "strongest identified pathway." |
| Report compiler | Chronology validator (mandatory gate), multidimensional per-gate conclusion ("Indeterminate-to-[level]"), historical patent-status normalization, expanded quality checklist. |
| Landscape skill | Design-space / sibling-filing analysis; historical legal-status language. |
| Glossary | All of the above codified; decision matrix updated with the new gates. |

## v1.5 changes

| Area | Change |
|---|---|
| Causal distance → **Mechanism distance** | C0–C4 renamed and redefined (C0 identical · C1 same mechanism minor variation · C2 same principle different intervention point · C3 different mechanism same effect · C4 fundamentally different). |
| **Design-choice distance (D0–D4)** | New orthogonal scale defined around the decision required, not novelty. D3 = cross-domain/application leap — a diagnostic, not an obviousness verdict. C and D are mandatory, reference-relative, orthogonal, **never combined** (reported `C2 / D3` per reference pathway). |
| **Negative Evidence Coverage Rule** | Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries a coverage object (scope, temporal scope, source domains, depth, completeness LOW/MEDIUM/HIGH/EXHAUSTIVE, limitations). Coverage is metadata, not evidence; never changes evidence state; HIGH coverage never auto-upgrades to CONFIRMED ABSENT; LOW + CONFIRMED ABSENT prohibited. CONFIRMED ABSENT requires a **bounded evidence universe**. Distinct semantics: NOT OBSERVED = negative search result · NOT IDENTIFIED = negative identification result · CONFIRMED ABSENT = bounded negative finding. |
| **Motivation Object** | Motivation gate becomes a first-class object per obviousness evidence object: categorized source lists (direct/analogous/inferred/contradicted — not counts), deterministic status derivation (GROUNDED / PARTIALLY GROUNDED / INFERRED / RECONCILIATION REQUIRED). Higher category never erases contradiction; analogies never accumulate into direct. |
| **Knowledge decomposition** | Evidence-stated separation of known component ≠ known function ≠ known combination ≠ known application. Lives in the Causal Bridge Test's prior_state; referenced by the evidence object. |
| **Causal Bridge Test** | New mandatory centerpiece of obviousness analysis: prior_state → claimed_state → required_change → bridge_evidence (post_filing excluded) → bridge_status (TRAVERSED / UNTRAVERSED / UNRESOLVED — UNRESOLVED is the default when motivation is INFERRED or application NOT OBSERVED). Obviousness Evidence Object becomes its audit trail. |
| **Overall patentability score removed** | Native output is the per-gate table only; no "Overall patentability" row in the default conclusion. Executive score ("Indeterminate-to-[level]") derived only on explicit request, labeled as a derived executive summary. Quality checklist gained the corresponding item. |
| Glossary / DIGEST / INDEX | All constructs codified; non-negotiables updated (8, 9, 10, 12, 13, 19 reworked; 23 added). |
| Skills 04, 06, 07 | Coverage object required on all negative landscape / literature / market findings. |

## v1.6 changes (2026-08-14) — Evidence Sufficiency Architecture (breaking change)

| Area | Change |
|---|---|
| Evidence ontology | Replaced the 7-state evidence ontology with the **three-layer architecture** (Evidence / Work / Analytical). Evidence layer: CONFIRMED PRESENT / CONFIRMED ABSENT only. Work layer: NOT_STARTED (internal) / SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED (avenue-level) / EXHAUSTED (proposition-level). Analytical layer: evidence → inference → conclusion; inference is never evidence. |
| Evidence Sufficiency Gate | Added as the **only admission path** for propositions into the report: schema-driven, atomic, with the proposition-identity firewall (steps 4 + 6) and schema-driven independent corroboration (independence_lineage_id). |
| Search Escalation Protocol | Fixed per-skill avenue checklists with deterministic priority; avenue_record audit schema; EXHAUSTED as a proposition-level termination state with the invariant that every required avenue is COMPLETE / BLOCKED / NOT_APPLICABLE (none REQUIRES_VERIFICATION). |
| Proposition-Schema Registry | Single authoritative registry of 10 schemas; skills reference schema IDs and may not duplicate or extend them. |
| Finding object | proposition_id + proposition_version, source_identity, independence_lineage_id, absence_basis (REQUIRED for CONFIRMED ABSENT). |
| Negative-evidence rule | Replaced the Negative Evidence Coverage Rule with the Evidence Sufficiency & Search Escalation Rule. |
| Terminal states | Removed UNRESOLVED as a terminal analytical conclusion; removed INFERRED / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / CONTESTED from active semantics. |
| Report architecture | Established Findings / Analytical Conclusions (premise maps; no orphan conclusions) / Operational Audit (barrier_type). Executive Summary ⊆ Established Findings + Analytical Conclusions. |
| verify.sh | Legacy-terminology semantic scan + root/package parity check. |
| Validation | Tesla US433,700 v1.6 rerun + negative-control test (see Test-report-results/). |

## v1.4 validation run (completed 2026-08-14)

End-to-end execution of the full 9-stage pipeline on Tesla US433,700 with live searches (Google Patents direct fetches + web literature search). Deliverable: `report-tesla-us433700-e2e-v14.md`.

**Validation results — all v1.4 gates exercised successfully:**

| Gate | Behavior observed |
|---|---|
| Evidence ontology | NOT OBSERVED / NOT IDENTIFIED / INFERRED used correctly and carried through all sections; no negative historical claim promoted to CONFIRMED ABSENT |
| E→I→C firewall | Finding structure produced for the obviousness proposition; inference strength kept at moderate (consistent with INFERRED motivation) |
| Motivation gate | Combination path flagged INFERRED → obviousness capped at UNRESOLVED |
| Causal-distance gate | C2 vs US424,036 (same principle, different intervention point); C3 vs US416,195 (different principle); mechanism displacement medium-to-high scored explicitly |
| Combination-obviousness exposure | Applied in place of "combination novelty" |
| Chronology validator | Caught the prior-art status of US424,036 (granted 1890-03-25, one day before filing); same-day sibling US433,702 and post-filing US433,703 correctly excluded |
| Multidimensional conclusion | "Indeterminate-to-moderate"; no compressed single label |
| Counterfactual exclusivity | Westinghouse framed as "strongest identified pathway" |

**Substantive finding of the run:** the earlier report missed US424,036 (Tesla's magnetic-lag motor, granted 1890-03-25), which discloses limitation (e) "retarding magnetization" directly. The novelty delta narrows to the interposed shield element (d). Direction of the conclusion is unchanged (Indeterminate-to-moderate) but the obviousness case is now stronger on (e) and still unresolved on (d).

## v1.5 validation run (completed 2026-08-14)

Re-execution of the full pipeline on Tesla US433,700 under v1.5. Deliverable: `report-tesla-us433700-e2e-v15.md`.

**Validation results — all v1.5 constructs exercised successfully:**

| Construct | Behavior observed |
|---|---|
| Mechanism + design-choice distance | C2/D3 vs US424,036 (same principle, different intervention point; application leap); C3/D3 vs US416,195 (different principle; application leap) — reported per pathway, never combined |
| Causal Bridge Test | Produced as the centerpiece of §4.6: prior_state (with knowledge decomposition) → claimed_state → required_change (D3 leap) → bridge_evidence (direct_pre_filing false; analogous true; post_filing excluded) → **bridge_status: UNRESOLVED** (application NOT OBSERVED, motivation not GROUNDED) |
| Motivation Object | First-class object with categorized source lists (direct empty; analogous = US424,036, US416,195, AIEE 1888; inferred = general knowledge; contradicted none) → deterministic derivation **PARTIALLY GROUNDED**; guardrails held (analogies did not accumulate into direct) |
| Negative Evidence Coverage Rule | Coverage objects on every NOT OBSERVED / NOT IDENTIFIED finding (§2.6, §5.4, §6.6, §8, Appendix D); none upgraded toward CONFIRMED ABSENT; no bounded universe claimed for adoption (stayed NOT OBSERVED, LOW coverage) |
| Knowledge decomposition | component/principle/function CONFIRMED PRESENT; combination/application NOT OBSERVED — the structural "known ≠ application" distinction exercised explicitly |
| Per-gate-only conclusion | No "Overall patentability" row in default §9.2 table; executive score only as derived-on-request §9.3 ("Indeterminate-to-moderate" derivation rule); quality checklist item enforced |
| Chronology validator | Passed — US424,036 granted 1890-03-25 (one day before filing) treated as prior art; same-day US433,702 and post-filing US433,703 excluded |
| Anti-pattern scan | Clean — banned phrases appear only as explanatory references to the v1.5 rules |

**Substantive finding:** unchanged in direction from v1.4 (obviousness Moderate, UNRESOLVED; bridge UNRESOLVED) — as expected, since the v1.5 constructs refine how the finding is evidenced and reported, not what the evidence says. The v1.5 upgrade is demonstrated: the conclusion is now decomposable into orthogonal, auditable dimensions (C/D, bridge_status, motivation status, coverage) that no longer compress into a scalar.

## Next action

The v1.5 end-to-end validation on Tesla US433,700 is complete and passed all gates (see above). Remaining: install into `~/.claude/skills/invention-evaluation-framework/` (or a project's `.claude/skills/`) and validate triggering with representative prompts before relying on it for live engagements.
