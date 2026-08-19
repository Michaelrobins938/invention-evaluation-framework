---
name: conduct-novelty-search
description: Runs a targeted prior-art search and produces a preliminary patentability assessment — utility, inventive step, and novelty — including claim-element mapping against flagged references. Use whenever a user asks if their invention is novel, wants a prior-art check, or wants claims compared against a specific reference patent. This is explicitly NOT a freedom-to-operate (FTO) / infringement search — if the user is asking whether they can legally sell their product without infringing someone else's in-force patent, redirect: that requires a different search scope (in-force claims, current legal status, broader claim reading) and a formal opinion from counsel, not this skill.
---

# Conduct Novelty Search

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- "Is my invention novel / patentable?"
- "What prior art exists for X?"
- "Compare my claims to this patent."

## When NOT to use — redirect instead
- "What patents might block me from selling this?" / "Can I get sued for making this?" — this is an FTO question. State plainly that FTO requires a distinct search (in-force claims only, current legal status, broader claim scope) and a formal infringement opinion from counsel, and that this skill's output should not be used as an FTO substitute even if it turns up relevant references.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. Every prior-art proposition uses the `prior_art_disclosure` schema from GLOSSARY.md; a finding row does not exist unless every required schema field is populated.

### 1. Claim construction layer
If formal claims are supplied, use them. If no formal claims exist:
- Construct a **provisional evaluation claim** for analytical purposes, explicitly labeled as such.
- Base it on the inventor's stated innovation claims and the technology profile from Skill 03.
- State clearly: "This is an analytical construct, not a legal claim construction."

### 2. Build search taxonomy
Core terms → broader terms → narrower terms → synonyms/alternates, cross-referenced against the IPC/CPC set from Skill 03.

### 3. Design 3–5 distinct queries
Each isolating a different combination of technical elements. A single query strategy under-recalls.

### 4. Run each query
Against a full-text patent database (e.g., Espacenet Worldwide) plus at least one classification-based search.

### 5. Abstract triage (≤90 seconds per result)
Title → abstract → keywords → relevance. Classify as: Irrelevant / Background / Related / Highly relevant / Potentially blocking. Record *why*.

### 6. Relationship layer (E0–E5) — structural only
For each flagged reference, classify its structural relationship to the invention (see GLOSSARY.md):
- E0: Unrelated
- E1: Same terminology/domain
- E2: Shared components
- E3: Same functional objective
- E4: Same causal architecture
- E5: Same mechanism

**Critical:** This is a structural taxonomy, not a legal score. E5 ≠ anticipation. E3 ≠ obviousness.

### 7. Claim-element mapping — mandatory for every "highly relevant" or "potentially blocking" result
**Direction: target claim → reference disclosure**

| Claim limitation | Reference disclosure | Status | Evidence |
|---|---|---|---|
| L1 | [passage or description] | Yes/No | Citation |
| L2 | [passage or description] | Yes/No | Citation |
| L3 | [passage or description] | Yes/No | Citation |
| L4 | [passage or description] | Yes/No | Citation |
| L5 | [passage or description] | Yes/No | Citation |

**Gate:**
- ALL = YES → ANTICIPATION candidate (high risk)
- ANY = NO → NOT ANTICIPATED. Move to obviousness analysis.

### 8. Obviousness analysis — Causal Bridge Test + structured evidence object
If any limitation is missing, produce the **Causal Bridge Test** (the mandatory centerpiece — states *what exactly has to be invented*), backed by the **Obviousness Evidence Object** (the audit trail — states *how we know*). See GLOSSARY.md for both templates.

**Causal Bridge Test** (per closest reference; the evidence object follows):

```yaml
causal_bridge_test:
  prior_state:
    known_objective: [evidence-stated]
    known_components: [evidence-stated]   # ← knowledge decomposition
    known_principles: [evidence-stated]   #   component/principle/function/
                                          #   combination/application
  claimed_state:
    claimed_configuration: [what the claim requires]
    claimed_effect: [what the claim achieves]
  bridge:
    required_change: [the exact step(s) between prior_state and claimed_state]
  bridge_evidence:
    direct_pre_filing: [true/false]
    analogous_pre_filing: [true/false]
    inventor_self_art: [true/false]
    general_science: [true/false]
    post_filing: excluded
  motivation: { ... }                        # ← first-class Motivation Object
  expectation_of_success:
    technical: [high/medium/low]
  unexpected_result:
    identified: [true/false]
    detail: [if true]
  bridge_status: [TRAVERSED | UNTRAVERSED]
  bridge_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]
```

**bridge_status:** TRAVERSED = evidence shows a skilled person would cross the bridge (obviousness strengthens); UNTRAVERSED = evidence shows the bridge was not reasonably crossable (non-obviousness argument). **When motivation or application evidence is insufficient, the bridge is not assessed as a conclusion** — the proposition enters the work layer (bridge_work_state: SEARCHING / ESCALATING / REQUIRES VERIFICATION / EXHAUSTED) until evidence is established or the avenue checklist is exhausted. UNRESOLVED is not a terminal state.

**Obviousness Evidence Object:**

```yaml
obviousness_case:
  closest_reference:
    patent_or_publication: [identifier]
    relevance: [E0–E5 classification]
    mechanism_distance: [C0–C4 from claimed mechanism]
    design_choice_distance: [D0–D4 — cross-domain/application leap is D3]
  knowledge_decomposition:
    component_known: [CONFIRMED PRESENT (source) | NOT ESTABLISHED (avenue record) | ...]
    principle_known: [CONFIRMED PRESENT (source) | ...]
    function_known: [CONFIRMED PRESENT (source) | ...]
    combination_known: [NOT ESTABLISHED (avenue record) | ...]
    application_known: [NOT ESTABLISHED (avenue record) | ...]
    motivation_to_combine: [GROUNDED | PARTIALLY GROUNDED | RECONCILIATION REQUIRED]
  search_escalation:                   # avenue checklist per GLOSSARY.md Search Escalation Protocol
    avenues:
      - id: A1
        name: primary_source_search
        priority: 1
        required: true
      - id: A2
        name: classification_search
        priority: 2
        required: true
      - id: A3
        name: citation_expansion
        priority: 3
        required: true
      - id: A4
        name: terminology_expansion
        priority: 4
        required: true
      - id: A5
        name: alternate_database
        priority: 5
        required: true
      - id: A6
        name: organizational_records
        priority: 6
        required: true
      - id: A7
        name: jurisdiction_specific_sources
        priority: 7
        required: true
      - id: A8
        name: independent_corroboration
        priority: 8
        required: true
  distinguishing_limitations:
    - limitation: [text]
      disclosed_in_closest: [yes/no]
      delta: [what is different]
  motivation:
    proposition: [the move a skilled person is asserted to have reason to make]
    direct:      [{source, support}]
    analogous:   [{source, support}]
    inferred:    [{source, support}]
    contradicted:[{source, support}]
    status: [GROUNDED | PARTIALLY GROUNDED | RECONCILIATION REQUIRED]
    work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]
  proposed_modification_paths:
    - type: [modification | combination | substitution | optimization]
      description: [what would be changed]
      prior_art_basis: [reference(s) that teach the change]
      motivation_delta: [only if this path materially differs from the shared motivation object]
      reasonable_expectation_of_success: [high/medium/low]
      compatibility_constraints: [any technical barriers]
  mechanism_displacement:
    prior_art_control_domain: [e.g., electrical_circuit | circuit_inductance]
    claimed_control_domain: [e.g., magnetic_material | saturation_shield]
    displacement: [low | medium | high]
    rationale: [why the causal intervention point moved]
  technical_effect:
    effect: [what the claimed invention achieves]
    evidence: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (avenue record)]
  unexpected_result: [yes/no/unknown]
  evidence_for_obviousness:
    - source: [citation]
      supports: [which part of the modification path]
  evidence_against_obviousness:
    - source: [citation]
      undermines: [which part]
  neutral_signals:
    - source: [citation]
      note: [observations that neither support nor undermine obviousness]
  unresolved_questions:
    - [any unanswered issues]
  evidence_state: [CONFIRMED PRESENT | CONFIRMED ABSENT]
  final_assessment: [Limited / Moderate / High obviousness risk — with rationale]
```

**Note:** If motivation, expectation-of-success, or the causal bridge cannot be evidenced, the obviousness proposition is not assessed as a conclusion — it is excluded from factual findings and recorded in the Operational Audit with barrier_type.

**Gates before any obviousness finding is stated:**

- **Motivation object.** The motivation gate is a first-class evidence object with categorized source lists (direct / analogous / inferred / contradicted) and a deterministic derivation: ≥1 direct no contradiction → GROUNDED; analogous only → PARTIALLY GROUNDED; inferred only → motivation not established (proposition enters the work layer); any contradiction → RECONCILIATION REQUIRED. Guardrails: a higher category never erases contradiction; analogies never accumulate into direct evidence. Paths with only inferred motivation (no direct or analogous source) cannot support an obviousness finding: the motivation proposition enters the work layer and escalates through the avenue checklist; if exhausted, the obviousness proposition is excluded from factual findings (see Operational Audit).
- **Expected-success gate.** reasonable_expectation_of_success must be consistent with the stated compatibility constraints — if the shield must be tuned, adds losses, or risks interfering with the rotating field, that caps the expectation and must be stated.
- **Causal Bridge Test gate.** The bridge must state the exact required_change between prior_state and claimed_state. If required_change is empty, that is anticipation territory, not obviousness. bridge_status is only TRAVERSED or UNTRAVERSED; when motivation or application evidence is insufficient, the bridge proposition enters the work layer.
- **Mechanism-distance and design-choice-distance gates.** Assess mechanism displacement (where the causal intervention point sits) plus mechanism distance (C0–C4) and design-choice distance (D0–D4) per reference pathway. High mechanism displacement and a D3 cross-domain/application leap are non-obviousness arguments and must be scored explicitly, never buried in prose. **C and D are never combined into a single score** — report as `C2 / D3`.
- **Coverage.** Every negative search result is recorded as avenue metadata in the avenue checklist. Coverage objects are replaced by avenue records. Search completion is not evidence.
- **Known principle ≠ obvious application.** "X was known" establishes a background principle, not an engineering application. The knowledge decomposition keeps `principle_known: CONFIRMED PRESENT` separate from `application_known: NOT ESTABLISHED (avenue record)`. The specific application step (e.g., "a skilled engineer would choose an insulated iron-wire shield interposed between coil and core as a controllable phase-delay mechanism") must be evidenced independently. If the specific application is not established in the record, the application proposition enters the work layer; if avenues are exhausted, the obviousness proposition is excluded from factual findings.

### 9. Unexpected-result check
Does the claimed combination produce a demonstrable unexpected technical result? (From Skill 03). If the performance-comparison data proposition cannot be established, it enters the work queue (escalate through the `performance_data` schema avenues); if exhausted, record in the Operational Audit with `barrier_type: insufficient_technical_demonstration`.

### 10. Distinguish "similar" from "important"
- "Similar" = title/abstract sounds alike.
- "Important" = actually reads on one or more claim limitations. Never let a title-level match stand for claim-level relevance.

### 11. Score per gate — axes, each with stated rationale and evidence status
- **Utility** — practical applicability (High/Moderate/Low). Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]
- **Inventive step** — is the delta over the closest reference non-obvious, accounting for mechanism displacement, mechanism distance (C0–C4), and design-choice distance (D0–D4)? (Limited/Moderate/High — or not established, see Operational Audit). Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]
- **Novelty** — is any single reference anticipatory, or only cumulative? (Low/Moderate/High). Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]

**Do not collapse these into a single "patentability" label, and do not produce an "overall patentability" row.** Report the per-gate table (see GLOSSARY.md, Multidimensional Decision Output). "Moderate obviousness risk" ≠ "moderate patentability" — they are not inverses. The native output is the per-gate table only. An executive score ("Indeterminate-to-[level]") is derived **only if the user explicitly requests one**, by the report compiler, labeled as a derived executive summary, always accompanied by the full per-gate table.

### 12. Self-prior-art exposure
If the closest references are the inventor's own earlier filings, assess:
- Anticipation exposure
- Obviousness exposure
- Double-patenting exposure
- Family/priority relationship

### 13. Combination-obviousness exposure (derivation risk)
If the invention's novelty rests on combining known elements, **do not call this "combination novelty"** — a combination can be completely novel while still being obvious. Frame it as **combination-obviousness exposure**: how readily can the claimed combination be reconstructed from the prior-art components, with a demonstrated motivation to combine? This is the most common basis for an obviousness rejection unless paired with a demonstrated unexpected result or synergy. State the derivation analysis explicitly: which components exist in prior art, which step is the delta, and whether that delta step is evidenced or only plausible.

### 14. Design-space position
Ask: what region of the inventor's design space does this invention occupy? Same-inventor sibling filings that implement the same higher-level architecture through different physical mechanisms indicate a design-space exploration event, not an isolated invention. Note this in the report — it reframes the invention from "is this patent novel?" to "where does this invention sit in the inventor's exploration of a design space?" This is contextual evidence, not a patentability score.

### 15. Decision matrix output
After completing the analysis, route through the state machine (including the motivation object / expected-success / causal-bridge-test / mechanism-distance + design-choice-distance / evidence-firewall gates) and output the conclusion with the structured obviousness evidence where applicable.

## v1.7 recovery and completeness contract

An unresolved anticipation proposition must not terminate at `NOT_ESTABLISHED` without
an evidence-recovery record. If continuity, same-assignee art, or a close product
lineage is detected, execute claim decomposition, critical-date filtering, family and
continuation traversal, applicant/examiner citation review, forward-citation review,
and prosecution-history review where available. Use explicit states:
`ANTICIPATION: ESTABLISHED`, `ANTICIPATION: NOT ESTABLISHED AFTER COMPLETE SEARCH`,
or `ANTICIPATION: UNRESOLVED — SEARCH-INCOMPLETE`. The last state is not a novelty
conclusion and must cap downstream patentability and IP confidence.

## Boundary
- Preliminary opinion only, based on abstract-level and partial claim review. Not a substitute for a formal patentability opinion from counsel.
- Does not cover non-patent literature — that's `conduct-literature-search`.
- Does not assess in-force legal status for infringement purposes. If FTO is requested, scope it as a separate engagement — do not fold it into this skill's output.
- **Evidence firewall:** nothing produced here may promote an inference into a fact. Every substantive finding uses the finding structure (proposition / evidence / inference / conclusion) from GLOSSARY.md, and downstream skills must carry each proposition with the evidence state it was established with — an unestablished proposition (work state EXHAUSTED, BLOCKED, or REQUIRES VERIFICATION) cannot later be cited as CONFIRMED PRESENT or CONFIRMED ABSENT; it can only be cited as an unestablished proposition with its avenue records.
- **Forward-citation counts are a neutral historical signal, not a patentability signal.** Low adoption/citation does not establish non-obviousness (the technology may be obvious, inferior, expensive, superseded, or commercially irrelevant). At most, a low count shows later technological lineage did not strongly converge on this mechanism. Never list low citation counts under evidence_against_obviousness; if included, put them in neutral_signals.
