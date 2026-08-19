```markdown
---
name: invention-evaluation-pipeline
description: Orchestrates the end-to-end evaluation of an invention, from submission to branded report, including technical analysis, patent landscape, novelty search, literature search, market opportunity, partner identification, compilation, and rendering. This skill combines all ten phases into a single comprehensive workflow. Use when performing a full evaluation or when a specific phase is needed, but the pipeline ensures dependency ordering and evidence discipline.
---

# Invention Evaluation Pipeline

## Core Principle

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

This pipeline is an **evidence-constrained invention reasoning engine**, not a collection of research prompts. The governing rule, enforced at every stage: **nothing downstream is allowed to promote an inference into a fact, and no proposition enters the report except through the Evidence Sufficiency Gate.** Every proposition carries a stable `proposition_id` + `proposition_version` and the evidence state it was established with (see GLOSSARY.md — Epistemic Architecture). The framework's job is to separate *what the evidence establishes* from *what the analyst wants to conclude* — and to prevent the two from merging.

## When to Use This Combined Skill
- "I have an invention — evaluate it end‑to‑end."
- "Run the full pipeline from submission to the final branded report."
- "I need a specific phase (e.g., novelty search, market analysis) — but also want to ensure dependencies are satisfied."

## When NOT to Use
- The user is asking for a single specific analysis without following the pipeline's evidence discipline — route to a dedicated skill or, if you are using this combined skill, still adhere to the phase’s constraints.

## Phase Completion & Routing
- Confirm whether a structured submission record already exists. If not, start with Phase 1.
- Check dependency status (hard dependencies must be satisfied before execution; soft dependencies can be bypassed with degraded capability, but note the degradation in the final report).
- Maintain a phase-completion checklist with explicit "blocked / needs-input" states.
- Route outputs to the next phase. Each routed output must preserve proposition identity: `proposition_id` + `proposition_version` + evidence state. Never strip, upgrade, or silently re‑scope a proposition at hand‑off; any refinement requires a version increment.
- If the user asks about FTO / infringement, stop and explain the distinction (see GLOSSARY.md) — do not proceed into the novelty pipeline as a substitute.
- **Final deliverable is the styled report.** After `compile-report` produces the report MD, ALWAYS render the branded "inventionevaluator" deliverable via `render-report` (Phase 9). Every end‑to‑end run ends with the styled HTML + A4 PDF — clean cover (wordmark + metadata block), TOC with accurate physical page numbers, running footer with page counters, CONFIDENTIAL watermark, gauges, SWOT, section dividers, search boxes. The renderer is presentation‑only: it never invents metrics, and every gauge/bar value must exist in the per‑run scores manifest with a basis proposition_id.

---

# Phase 1: Gather Invention Submission

## When to Use
- A user shares an invention description, upload, or disclosure form.
- A user asks what information you need to start an evaluation.

## When NOT to Use
- A structured submission record already exists for this invention — go straight to Phase 2.

## Fields to Capture

**Mandatory**
- Invention name
- Short description (1–2 sentences)
- Detailed description
- Background / related research the inventor is aware of
- Innovation claims (what the inventor believes is new)

**Critical secondary**
- Proof-of-concept status
- Current IP status (filed, provisional, unfiled, licensed)
- Target products/services and markets
- Known competitors

**Mandatory — disclosure timing**
Capture every public talk, publication, demonstration, sale offer, or social‑media post about the invention, each with a date. This is the single highest‑leverage field in the entire intake: it can determine whether a filing deadline has already passed. If the inventor states there has been no disclosure, record that as "CONFIRMED ABSENT (per inventor statement)" — the bounded universe is the inventor's own statement, with `absence_basis` noted — rather than leaving the field blank; a blank field and a confirmed "none" are not the same thing for audit purposes. **Distinguish the two cases:** an inventor's direct statement of no disclosure is CONFIRMED ABSENT (bounded universe: inventor statement, single source); a search that found no disclosure is a search‑result record (avenue metadata) — it establishes nothing about the world and never upgrades to CONFIRMED ABSENT. If a search‑based absence is needed, it must go through the Evidence Sufficiency Gate with a bounded universe.

## Execution
1. Elicit each mandatory field; do not infer values the inventor hasn't stated.
2. Explicitly ask about disclosure timing even if not volunteered — inventors routinely underreport this.
3. Flag any missing field rather than filling it with a plausible guess.
4. Output the record as a structured table or YAML block so downstream skills can consume it directly.
5. If any disclosure date appears close to or past a jurisdiction's grace‑period limit, flag this immediately for escalation rather than continuing silently through the pipeline.

## Boundary
- This phase records claims; it does not validate, search, or judge them.
- No patentability or market opinion at this stage.

---

# Phase 2: Analyze Technology Fundamentals

## When to Use
- A structured submission record exists and the next step is characterizing the technology.
- The user asks for a feature‑benefit table, an innovation assessment, or a regulatory‑burden estimate.

## When NOT to Use
- The user is asking you to run a patent or literature search — that consumes this phase's output but is a separate phase.

## Execution
1. **Idea description.** Write one plain‑language paragraph. This seeds every downstream search‑term list.
2. **Rapid domain orientation (30‑minute cap).** Read a review article or high‑level reference for the field; extract 5–10 terms practitioners actually use; explicitly note what you don't yet understand. The goal is "search‑competent," not subject‑matter expertise.
3. **Feature‑benefit map.** Every feature row must resolve to a stated user‑facing benefit — a feature with no benefit is incomplete.
4. **Innovation assessment — answer explicitly:**
   - What differs from known approaches?
   - Is any part of the novelty a *combination* of known elements? (Flag this as **combination‑obviousness exposure**, not "combination novelty" — a combination can be completely novel while still being obvious. The operative question is derivation risk: how readily can the combination be reconstructed from prior‑art components with a demonstrated motivation to combine? This is the weakest basis for an inventive‑step argument absent an unexpected result.)
   - What specific technical elements are claimed as unique?
   - **Design‑space position:** does the inventor appear to be exploring multiple physical implementations of the same higher‑level architecture (sibling filings, alternative mechanisms)? Note where this invention sits in that exploration.
5. **Unexpected‑result gate.** Does the claimed combination produce a demonstrable unexpected technical result? (CONFIRMED PRESENT / CONFIRMED ABSENT — or not established, see Operational Audit). If the performance data proposition cannot be established, it enters the work queue: escalate through the `performance_data` schema avenues; if exhausted, record in the Operational Audit with `barrier_type: insufficient_technical_demonstration`.
6. **Regulatory burden.** Estimate Low/Med/High per relevant jurisdiction using the `regulatory_regime` schema: governing statute/regulation (exact identifier) + why the technology falls inside/outside it. A regulatory rating without the governing regime is not a finding — it is an unestablished proposition.
7. **Development stage.** Classify Concept → Prototype → Validation → Pilot → Commercialization; if pre‑prototype, list concrete next milestones with rough timelines.
8. **Classification seed.** Derive an initial IPC/CPC candidate set from the idea description, each candidate with its exact code, official title, and source (official classification authority). A guessed classification is not a finding — candidates are hypotheses for the landscape search, not established classifications.
9. **Proposition ledger.** Register every substantive proposition this phase produces (performance data, regulatory regime, classification candidates) with a `proposition_id` + `proposition_version` + schema reference, per GLOSSARY.md.
10. **Mandatory output: "what I still don't understand."** This list drives later escalation decisions — don't omit it even if short.

## Boundary
- No search is performed here.
- Regulatory output is scoping‑level, not a substitute for regulatory counsel.
- Development‑stage timelines are estimates pending expert review.

---

# Phase 3: Conduct Patent Landscape

## When to Use
- The user wants competitive/field‑level patent context: volume, geography, assignees, trend.

## When NOT to Use
- The user wants to know if their specific invention is novel or infringes — use Phase 5 instead.

## Execution
1. Select a primary database (e.g., WIPO PatentScope) and at least one secondary source (e.g., Espacenet, Derwent) for cross‑validation. Single‑source landscaping systematically under‑recalls — don't skip the second source.
2. Build the query from the classification candidates and core terms produced by Phase 2.
3. **Temporal search calibration.** Determine search window based on invention date and field history, not a fixed 10–15 year window:
   - Modern fast‑moving field → recent window + historical foundational art
   - Mature field → broader historical window
   - Historical invention (e.g., pre‑1900) → prior‑art window extending to earliest relevant technical development
   - Unknown date → establish temporal anchor first
4. For each major assignee or result cluster, note: priority date vs. filing vs. publication date; whether a patent family spans multiple jurisdictions; legal status (pending/granted/expired/abandoned — never skip this); and forward/backward citation signal where available. **For historical patents, do not import modern legal‑status labels unexamined** — distinguish patent grant → historical term under applicable law → expiration, and prefer "Historical term expired: [date] (17 years from grant, subject to the historical patent regime)" over "Expired — Lifetime."
5. Extract: total family count, jurisdictional distribution, top assignees and share, CPC/IPC subclass concentration, filing trend by year.
6. Produce or describe visualizations: geographic split, assignee bar chart, time‑trend line.
7. **Design‑space / sibling analysis.** Identify same‑inventor filings that implement the same higher‑level architecture through different physical mechanisms (e.g., independent circuits vs. self‑induction vs. magnetic shielding vs. core lamination). These indicate a design‑space exploration event. Report the invention's position in that space — it reframes the evaluation from "is this patent novel?" to "what region of the inventor's design space does this occupy?" This is contextual evidence, not a patentability score.
8. **Negative landscape findings go through the escalation protocol.** If the landscape search returns no filings for a proposition (e.g., "no filings found in jurisdiction X"), the proposition does not become a finding. Run the skill's avenue checklist (primary source → classification search → citation expansion → terminology expansion → alternate database → organizational records → jurisdiction‑specific sources → independent corroboration), logging each avenue record. Only when every required avenue is dispositioned (COMPLETE / BLOCKED / NOT_APPLICABLE) may the proposition be marked EXHAUSTED — and EXHAUSTED is not evidence: the proposition is excluded from factual findings and recorded in the Operational Audit with `barrier_type` (e.g., `insufficient_search_completion`). Single‑source landscaping is one avenue, not exhaustion. CONFIRMED ABSENT additionally requires a bounded universe + absence_basis.
9. **Avenue checklist (mandatory for every negative landscape proposition).** Use the default avenue template from GLOSSARY.md (Search Escalation Protocol), customized for landscape propositions: A1 primary patent database (e.g., WIPO PatentScope), A2 classification search (CPC/IPC), A3 citation expansion, A4 terminology expansion, A5 alternate database (e.g., Espacenet, Derwent), A6 organizational records (assignee filings), A7 jurisdiction‑specific sources, A8 independent corroboration. Each avenue carries an `avenue_record` with searches_run, sources_consulted, relevant_results, exclusions, limitations, completion_basis.
10. Interpret concentration signals explicitly, e.g.:
   - Academic‑assignee dominance → early‑stage research activity, not commercial saturation.
   - A small number of dominant assignees → consolidated field, elevated risk of blocking patents.
   - Sharp filing growth in the last 3–5 years → hot field, expect high prior‑art density in the novelty search.

## Mandatory Classification and Quantitative‑Data Gate

Before any CPC/NAICS code is used for quantitative landscape or market data:

1. Start from the classification printed on the patent front page and structured submission record. Never substitute a more available or higher‑volume class.
2. Fetch the plain‑English title for each candidate CPC/NAICS code and test thematic consistency against the invention description. A failed test is a hard block.
3. Record `classification-in`, `classification-verified`, and `pass/fail` in the avenue ledger, including the source used for the title check.
4. Narrow patent queries with invention‑specific keywords in addition to the verified CPC code. Bare subclass totals are not invention‑specific evidence.
5. Render `not established` only after a logged query was actually issued and returned zero, unusable, or unverifiable results. The ledger must preserve query, source, result count, and rejection reason. An unissued query is a pipeline defect.

## v1.7 Recovery Escalation

When the target has same‑assignee references, continuity, or a named commercial product, the landscape run must escalate beyond retrieval volume:

1. Reconstruct the patent family and parent/divisional/continuation relationships.
2. Review applicant/examiner citations and forward citations where available.
3. Normalize assignee variants and group publication records into families.
4. Separate retrieval volume, normalized landscape, and analytical inference in the output.
5. Follow named assignee/product/company breadcrumbs into ownership, commercialization, regulatory, and current‑status records.

If any required path is not attempted, the proposition state is `ESCALATION_REQUIRED`, not `SEARCH_EXHAUSTED`.

## Boundary
- Establishes context only — not a novelty or infringement determination.
- Result quality is bounded by query quality; refine iteratively rather than accepting a single pass.

---

# Phase 4: Conduct Literature Search

## When to Use
- "Find papers on X."
- "What's the state of research on Y?"
- Complementing a novelty search with non‑patent prior art.

## When NOT to Use
- The question is specifically about patents — use Phase 3 or Phase 5.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

1. Derive search terms from the idea description produced by Phase 2, plus modifiers for adjacent technical approaches.
2. Run 3–5 queries spanning broad‑field and specific‑mechanism searches.
3. **Abstract triage, 30–90 seconds per paper:** title → abstract first sentence → abstract last sentence → keywords if still uncertain. Classify as Irrelevant / Background / Supporting / Potentially Conflicting / Prior Art Risk.
4. For flagged items, capture the full `literature_disclosure` schema from GLOSSARY.md: authors, title, venue, date, DOI/report number, URL, experimental system, cooling/technology, application, what was actually demonstrated, and a relevance note stating specifically which element of the invention it touches. A row without publication identity (authors, title, venue, date, DOI) does not exist. A generic "seems related" note is not usable downstream.
5. Treat any dated non‑patent disclosure (conference talk, preprint, thesis) with the same rigor as a patent reference for prior‑art and filing‑deadline purposes.
6. Summarize the literature landscape in terms the patentability opinion can use directly — e.g., state plainly if a combination the invention relies on for novelty is already independently reported in the literature.
7. **Evidence‑state discipline (v1.6).** Evidence layer: CONFIRMED PRESENT / CONFIRMED ABSENT only. Work layer: SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED (avenue) / EXHAUSTED (proposition). A search that returns nothing is avenue metadata, not evidence. CONFIRMED ABSENT requires a bounded universe + absence_basis. See GLOSSARY.md — Epistemic Architecture.
8. **Negative literature findings go through the escalation protocol.** If a proposition (e.g., "no pre‑filing publication discloses the claimed mechanism") is not established, run the skill's avenue checklist (A1 primary source search → A2 classification search → A3 citation expansion → A4 terminology expansion → A5 alternate database → A6 organizational records → A7 jurisdiction‑specific sources → A8 independent corroboration), logging each avenue_record. Only when every required avenue is dispositioned may the proposition be marked EXHAUSTED — and EXHAUSTED is not evidence: the proposition is excluded from factual findings and recorded in the Operational Audit with barrier_type. State the databases and date ranges actually searched in each avenue record (e.g., "IEEE Xplore 1880–1900, Google Scholar full range, domain: electrical engineering history").
9. **Known principle ≠ obvious application.** If the literature confirms a background principle (e.g., "magnetic saturation was known") but does not disclose the specific engineering application (e.g., "an interposed iron‑wire shield used as a controllable phase‑delay mechanism in an AC motor"), record the principle as CONFIRMED PRESENT and the application as NOT ESTABLISHED (avenue record); the application proposition escalates through the avenue checklist if it matters to a conclusion. Do not let the confirmed principle carry the application's evidentiary weight.

## v1.7 Recovery Escalation

Literature gaps trigger recovery rather than immediate termination. For implantable medical devices, escalate from invention‑specific papers to engineering validation, hermetic packaging, feedthrough reliability, electrode degradation, inflammation, wireless power, and long‑term encapsulation literature. Search both supporting and contradicting evidence. If a technical database or full text is unavailable, record the query, source, result, and alternate path before assigning `SEARCH_EXHAUSTED`.

- One database (e.g., Google Scholar) is not exhaustive; supplement with domain‑specific sources (PubMed, IEEE Xplore, etc.) where the field warrants it.
- If a flagged paper requires technical background beyond your domain orientation to assess, say so and flag for escalation rather than guessing at its significance.

## Boundary
- This phase does not replace a formal patentability opinion.

---

# Phase 5: Conduct Novelty Search

## When to Use
- "Is my invention novel / patentable?"
- "What prior art exists for X?"
- "Compare my claims to this patent."

## When NOT to Use — Redirect Instead
- "What patents might block me from selling this?" / "Can I get sued for making this?" — this is an FTO question. State plainly that FTO requires a distinct search (in‑force claims only, current legal status, broader claim scope) and a formal infringement opinion from counsel, and that this phase's output should not be used as an FTO substitute even if it turns up relevant references.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. Every prior‑art proposition uses the `prior_art_disclosure` schema from GLOSSARY.md; a finding row does not exist unless every required schema field is populated.

### 1. Claim construction layer
If formal claims are supplied, use them. If no formal claims exist:
- Construct a **provisional evaluation claim** for analytical purposes, explicitly labeled as such.
- Base it on the inventor's stated innovation claims and the technology profile from Phase 2.
- State clearly: "This is an analytical construct, not a legal claim construction."

### 2. Build search taxonomy
Core terms → broader terms → narrower terms → synonyms/alternates, cross‑referenced against the IPC/CPC set from Phase 2.

### 3. Design 3–5 distinct queries
Each isolating a different combination of technical elements. A single query strategy under‑recalls.

### 4. Run each query
Against a full‑text patent database (e.g., Espacenet Worldwide) plus at least one classification‑based search.

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

### 7. Claim‑element mapping — mandatory for every "highly relevant" or "potentially blocking" result
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
    known_objective: [evidence‑stated]
    known_components: [evidence‑stated]   # ← knowledge decomposition
    known_principles: [evidence‑stated]   #   component/principle/function/
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
  motivation: { ... }                        # ← first‑class Motivation Object
  expectation_of_success:
    technical: [high/medium/low]
  unexpected_result:
    identified: [true/false]
    detail: [if true]
  bridge_status: [TRAVERSED | UNTRAVERSED]
  bridge_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]
```

**bridge_status:** TRAVERSED = evidence shows a skilled person would cross the bridge (obviousness strengthens); UNTRAVERSED = evidence shows the bridge was not reasonably crossable (non‑obviousness argument). **When motivation or application evidence is insufficient, the bridge is not assessed as a conclusion** — the proposition enters the work layer (bridge_work_state: SEARCHING / ESCALATING / REQUIRES VERIFICATION / EXHAUSTED) until evidence is established or the avenue checklist is exhausted. UNRESOLVED is not a terminal state.

**Obviousness Evidence Object:**

```yaml
obviousness_case:
  closest_reference:
    patent_or_publication: [identifier]
    relevance: [E0–E5 classification]
    mechanism_distance: [C0–C4 from claimed mechanism]
    design_choice_distance: [D0–D4 — cross‑domain/application leap is D3]
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

**Note:** If motivation, expectation‑of‑success, or the causal bridge cannot be evidenced, the obviousness proposition is not assessed as a conclusion — it is excluded from factual findings and recorded in the Operational Audit with barrier_type.

**Gates before any obviousness finding is stated:**

- **Motivation object.** The motivation gate is a first‑class evidence object with categorized source lists (direct / analogous / inferred / contradicted) and a deterministic derivation: ≥1 direct no contradiction → GROUNDED; analogous only → PARTIALLY GROUNDED; inferred only → motivation not established (proposition enters the work layer); any contradiction → RECONCILIATION REQUIRED. Guardrails: a higher category never erases contradiction; analogies never accumulate into direct evidence. Paths with only inferred motivation (no direct or analogous source) cannot support an obviousness finding: the motivation proposition enters the work layer and escalates through the avenue checklist; if exhausted, the obviousness proposition is excluded from factual findings (see Operational Audit).
- **Expected‑success gate.** reasonable_expectation_of_success must be consistent with the stated compatibility constraints — if the shield must be tuned, adds losses, or risks interfering with the rotating field, that caps the expectation and must be stated.
- **Causal Bridge Test gate.** The bridge must state the exact required_change between prior_state and claimed_state. If required_change is empty, that is anticipation territory, not obviousness. bridge_status is only TRAVERSED or UNTRAVERSED; when motivation or application evidence is insufficient, the bridge proposition enters the work layer.
- **Mechanism‑distance and design‑choice‑distance gates.** Assess mechanism displacement (where the causal intervention point sits) plus mechanism distance (C0–C4) and design‑choice distance (D0–D4) per reference pathway. High mechanism displacement and a D3 cross‑domain/application leap are non‑obviousness arguments and must be scored explicitly, never buried in prose. **C and D are never combined into a single score** — report as `C2 / D3`.
- **Coverage.** Every negative search result is recorded as avenue metadata in the avenue checklist. Coverage objects are replaced by avenue records. Search completion is not evidence.
- **Known principle ≠ obvious application.** "X was known" establishes a background principle, not an engineering application. The knowledge decomposition keeps `principle_known: CONFIRMED PRESENT` separate from `application_known: NOT ESTABLISHED (avenue record)`. The specific application step (e.g., "a skilled engineer would choose an insulated iron‑wire shield interposed between coil and core as a controllable phase‑delay mechanism") must be evidenced independently. If the specific application is not established in the record, the application proposition enters the work layer; if avenues are exhausted, the obviousness proposition is excluded from factual findings.

### 9. Unexpected‑result check
Does the claimed combination produce a demonstrable unexpected technical result? (From Phase 2). If the performance‑comparison data proposition cannot be established, it enters the work queue (escalate through the `performance_data` schema avenues); if exhausted, record in the Operational Audit with `barrier_type: insufficient_technical_demonstration`.

### 10. Distinguish "similar" from "important"
- "Similar" = title/abstract sounds alike.
- "Important" = actually reads on one or more claim limitations. Never let a title‑level match stand for claim‑level relevance.

### 11. Score per gate — axes, each with stated rationale and evidence status
- **Utility** — practical applicability (High/Moderate/Low). Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]
- **Inventive step** — is the delta over the closest reference non‑obvious, accounting for mechanism displacement, mechanism distance (C0–C4), and design‑choice distance (D0–D4)? (Limited/Moderate/High — or not established, see Operational Audit). Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]
- **Novelty** — is any single reference anticipatory, or only cumulative? (Low/Moderate/High). Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]

**Do not collapse these into a single "patentability" label, and do not produce an "overall patentability" row.** Report the per‑gate table (see GLOSSARY.md, Multidimensional Decision Output). "Moderate obviousness risk" ≠ "moderate patentability" — they are not inverses. The native output is the per‑gate table only. An executive score ("Indeterminate‑to‑[level]") is derived **only if the user explicitly requests one**, by the report compiler, labeled as a derived executive summary, always accompanied by the full per‑gate table.

### 12. Self‑prior‑art exposure
If the closest references are the inventor's own earlier filings, assess:
- Anticipation exposure
- Obviousness exposure
- Double‑patenting exposure
- Family/priority relationship

### 13. Combination‑obviousness exposure (derivation risk)
If the invention's novelty rests on combining known elements, **do not call this "combination novelty"** — a combination can be completely novel while still being obvious. Frame it as **combination‑obviousness exposure**: how readily can the claimed combination be reconstructed from the prior‑art components, with a demonstrated motivation to combine? This is the most common basis for an obviousness rejection unless paired with a demonstrated unexpected result or synergy. State the derivation analysis explicitly: which components exist in prior art, which step is the delta, and whether that delta step is evidenced or only plausible.

### 14. Design‑space position
Ask: what region of the inventor's design space does this invention occupy? Same‑inventor sibling filings that implement the same higher‑level architecture through different physical mechanisms indicate a design‑space exploration event, not an isolated invention. Note this in the report — it reframes the invention from "is this patent novel?" to "where does this invention sit in the inventor's exploration of a design space?" This is contextual evidence, not a patentability score.

### 15. Decision matrix output
After completing the analysis, route through the state machine (including the motivation object / expected‑success / causal‑bridge‑test / mechanism‑distance + design‑choice‑distance / evidence‑firewall gates) and output the conclusion with the structured obviousness evidence where applicable.

## v1.7 Recovery and Completeness Contract

An unresolved anticipation proposition must not terminate at `NOT_ESTABLISHED` without an evidence‑recovery record. If continuity, same‑assignee art, or a close product lineage is detected, execute claim decomposition, critical‑date filtering, family and continuation traversal, applicant/examiner citation review, forward‑citation review, and prosecution‑history review where available. Use explicit states:
`ANTICIPATION: ESTABLISHED`, `ANTICIPATION: NOT ESTABLISHED AFTER COMPLETE SEARCH`,
or `ANTICIPATION: UNRESOLVED — SEARCH‑INCOMPLETE`. The last state is not a novelty conclusion and must cap downstream patentability and IP confidence.

## Boundary
- Preliminary opinion only, based on abstract‑level and partial claim review. Not a substitute for a formal patentability opinion from counsel.
- Does not cover non‑patent literature — that's Phase 4.
- Does not assess in‑force legal status for infringement purposes. If FTO is requested, scope it as a separate engagement — do not fold it into this phase's output.
- **Evidence firewall:** nothing produced here may promote an inference into a fact. Every substantive finding uses the finding structure (proposition / evidence / inference / conclusion) from GLOSSARY.md, and downstream phases must carry each proposition with the evidence state it was established with — an unestablished proposition (work state EXHAUSTED, BLOCKED, or REQUIRES VERIFICATION) cannot later be cited as CONFIRMED PRESENT or CONFIRMED ABSENT; it can only be cited as an unestablished proposition with its avenue records.
- **Forward‑citation counts are a neutral historical signal, not a patentability signal.** Low adoption/citation does not establish non‑obviousness (the technology may be obvious, inferior, expensive, superseded, or commercially irrelevant). At most, a low count shows later technological lineage did not strongly converge on this mechanism. Never list low citation counts under evidence_against_obviousness; if included, put them in neutral_signals.

---

# Phase 6: Analyze Market Opportunity

## When to Use
- "What's the market for this?" / "Who are my competitors?" / "Build a SWOT."

## When NOT to Use
- The question is really about patent assignees or filing activity — use Phase 3.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

1. Identify primary markets (direct, adjacent, future) with size and CAGR using the `market_sizing` schema from GLOSSARY.md: market boundary, geography, time period, figure, source, reconciliation, derivation. **A quantitative figure that cannot be reconstructed from an identified source must not appear** — the proposition fails the Sufficiency Gate and enters the work queue (escalate through the avenue checklist; if exhausted, record in the Operational Audit with `barrier_type: insufficient_identity` or `source_unavailable`). If the only available evidence is qualitative (e.g., "AC infrastructure was expanding rapidly in this period"), say that — it is more useful than an impressive‑looking number with no reconstructable basis. Derived figures are analytical inferences, labeled as such, never evidence states.
1b. **Market relevance / demand propositions** (e.g., "government procurement activity existed for this technology") use the `market_relevance_award` or `market_relevance_report` schema: agency/publisher, award_id/report_id, recipient, date, title, URL, relevant passage, independence_lineage_id — with ≥2 independent sources. "Various SBIR awards…" with no award identities is not a finding; it is an unestablished proposition that escalates through the avenue checklist.
2. Assign a NAICS (or regional equivalent) code using the `naics_classification` schema: taxonomy_source (official NAICS/Census documentation), exact code, official title, edition year, and basis (official definition match / activity match / product‑manufacturing match). **Never guess a classification.** If the official taxonomy record cannot be established, the classification proposition is excluded from factual findings and recorded in the Operational Audit with `barrier_type: insufficient_identity` — no code is reported.
3. Pull industry trend data — establishment count, employment, shipment value — over a multi‑year window.
4. Define the opportunity structure: product/service, need, purchaser vs. end consumer, distribution channel, price point, purchase frequency.
5. **Score commercial actionability, not just size.** A technology can be technically interesting without being commercially actionable — no clear buyer, cost of production too high, regulatory pathway out of reach, or solving a problem nobody will pay to fix. Score each opportunity on: market size (low/med/high) × growth (low/med/high) × accessibility (low/med/high) × competitive intensity (low/med/high). Two or more "low" scores → flag as high‑risk and say so plainly; don't soften it into a recommendation to proceed without a stated mitigating factor.
6. **Technical maturity vs. commercial readiness — separate explicitly:**
   - Patent disclosure: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - Engineering feasibility: High/Med/Low (with evidence state)
   - Prototype evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - Production evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - Commercial adoption evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)
   - **Adoption is established only through the `commercial_adoption` schema**: a product‑identity link (the commercial product is identifiable as embodying the claimed technology), source, date, and ≥2 independent sources (MATERIAL_PROVENANCE_INDEPENDENCE). Absence of adoption evidence is not a finding — the proposition enters the work queue; if avenues are exhausted, it is excluded from factual findings and recorded in the Operational Audit. CONFIRMED ABSENT requires a bounded evidence universe + absence_basis.
   - **Negative findings go through the escalation protocol.** Every unestablished market proposition (adoption, market relevance, market sizing) runs the skill's avenue checklist (A1 primary source search → A2 classification search → A3 citation expansion → A4 terminology expansion → A5 alternate database → A6 organizational records → A7 jurisdiction‑specific sources → A8 independent corroboration), logging each avenue_record with the records actually searched (e.g., "commercial adoption of the shield mechanism in US433,700, 1890–1907, avenue records: patent records + historical company records + technical literature; Westinghouse production records BLOCKED — alternate access routes attempted"). EXHAUSTED is not evidence; the proposition is excluded from factual findings.
   - **Commercial readiness:** State "NOT ESTABLISHED" unless adoption evidence passes the Sufficiency Gate; the readiness proposition otherwise enters the work queue.
7. Map the competitive landscape (direct, indirect, future competitors), including each competitor's known IP posture — cross‑reference Phase 3 output where available rather than re‑deriving it.
8. Build a SWOT. Weaknesses and threats are mandatory fields, not optional ones.
9. **Counterfactual‑exclusivity audit.** Audit every statement of the form "only partner," "no other pathway," "without X, impossible." Replace with "strongest identified pathway" formulations. Claiming that only one commercialization pathway exists is a claim about the absence of alternatives — which is almost never evidenced. If the record shows one strong path and others unidentified, say exactly that.

## Mandatory Classification and Quantitative‑Data Gate

Before any NAICS/CPC code is used for market or industry metrics:

1. Start from the classification printed on the patent front page and structured submission record. Never substitute a more available or higher‑volume class.
2. Fetch the plain‑English title for each candidate code and test thematic consistency against the invention description. A failed test is a hard block; reject the code.
3. Record `classification-in`, `classification-verified`, and `pass/fail` in the avenue ledger with the source used for the title check.
4. Pull Census establishment, employment, shipment, or revenue data only for the verified NAICS code. Do not publish raw classification‑level totals as invention market data.
5. Render `not established` only after a logged query was actually issued and returned zero, unusable, or unverifiable results. Preserve query, source, result count, and rejection reason in the avenue ledger. An unissued query is a pipeline defect.

## v1.7 Commercial Recovery and Lifecycle Analysis

Do not terminate at missing TAM, revenue, reimbursement, or adoption data. Build bounded patient‑population and procedure‑economics models using public proxies, and trace named products through clinical trials, regulatory pathways, reimbursement, company history, and market outcome. Classify unresolved commercialization history as technical, regulatory, reimbursement, market, timing, business‑model, or undetermined failure. Then evaluate technology‑resurrection paths created by changes in manufacturing, AI, batteries, clinical practice, or regulation. Every proxy carries a decision‑value label.

## Boundary
- Not a financial model — no NPV or breakeven calculation.
- SWOT judgments must trace back to evidence from the technology and landscape phases, not be asserted independently.
- If market data is genuinely insufficient to score actionability, the proposition is not established: escalate through the avenue checklist; if exhausted, exclude from factual findings and record in the Operational Audit. **Never present an unsourced quantitative claim (revenue, CAGR) as a fact — omit it or record it as an unestablished proposition.**
- Patent granted ≠ commercialization. Assignment ≠ commercialization. Technical plausibility ≠ commercialization.

---

# Phase 7: Identify Partners

## When to Use
- "Who should I license this to?" / "Find potential partners."

## When NOT to Use
- The ask is purely about competitors, with no partnership intent — use Phase 6.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. A partner‑fit proposition that cannot satisfy the `partner_fit` schema escalates through the avenue checklist; if exhausted, it is excluded from factual findings and recorded in the Operational Audit.

1. Draw candidates from the Phase 6 competitive landscape, then expand to adjacent players not captured there — distributors, clinical partners, research collaborators.
2. For each candidate, capture the `partner_fit` schema from GLOSSARY.md: what they sell, what they buy, their technical need, and the mapping to the invention (why *this* invention would interest *this* company specifically, not a generic fit statement) — each field with source_identity. A candidate row without the sell/buy/need/mapping fields does not exist. Also capture: organization and website; contact person and role if known; proposed partnership model (licensing, JV, R&D collaboration).
3. Prioritize High/Medium/Low fit, with the reasoning stated, not just the label.
4. **Counterfactual‑exclusivity audit.** Any statement that one partner is "the only" viable path, or that "without X there is no commercial vehicle," is a claim about the absence of alternatives — almost never evidenced. Reformulate as "the strongest identified pathway" and explicitly note that alternatives were not established (see Operational Audit) rather than established not to exist. Penalize exclusivity framing unless absence of alternatives is itself evidenced.

## v1.7 Rights‑State Contract

Partner recommendations must consume the rights graph before selecting a primary strategy. An expired or lapsed patent blocks an unqualified standalone patent‑licensing recommendation and activates portfolio, surviving‑family, know‑how, regulatory‑asset, clinical‑data, and historical‑technology diligence. Every recommendation records the legal‑status dependency and remaining evidence debt.

## Boundary
- Research output only — no outreach, and no sharing of confidential invention detail without an NDA in place.
- Contact information requires verification before use; treat it as a starting point, not a validated list.

---

# Phase 8: Compile Report

## When to Use
- "Generate the final report." / "Put it all together." / "Prepare the deliverable."

## When NOT to Use
- Any section's underlying analysis hasn't been run yet — invoke that phase first rather than fabricating the section here.

## Execution

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. This phase compiles only — it never converts an unestablished proposition into a factual claim.

1. Collect all upstream outputs. If any are missing, say so and either invoke the missing phase or explicitly mark the section "NOT ESTABLISHED" in the report — never fill a gap with invented content.
1a. **Write the compiled Markdown to the resolved run directory before delivery.** The report compiler must receive an absolute output path from the engine artifact‑destination gate. If no path is supplied, compilation is blocked; do not return an unsaved report as if it were a deliverable.
2. **Run the chronology validator before writing anything.** Cross‑check every date in the submission record and upstream outputs: filing date, priority date, disclosure dates, sale‑offer dates, grant date, and any "before [date]" phrasing. Every "before X" must be consistent with the actual filing date. Flag and fix any mismatch (e.g., a section saying "before May 26, 1890" when the filing was March 26, 1890). This is a mandatory gate, not a style preference.
3. Write a 1–2 page executive summary **constrained to Established Findings + Analytical Conclusions** (Executive Summary ⊆ Established Findings + Analytical Conclusions). It may reference the Operational Audit ("Several evidentiary gaps remain and are documented in the Operational Audit") but never convert audit content into factual prose. Label it as a derived executive summary.
4. Assemble the body in standard order: Executive Summary → Technology Analysis → Landscape Analysis → IP/Novelty Analysis → Market Analysis → Opportunity Assessment → Potential Partners → Appendices.
5. Include all tables and figures generated upstream rather than re‑summarizing them in prose.
6. **Mandatory: Established Findings section.** Only rows that passed the Evidence Sufficiency Gate (CONFIRMED PRESENT / CONFIRMED ABSENT), each rendered from its finding object with full provenance (proposition_id, source_identity, locator, absence_basis where applicable).
7. **Mandatory: Analytical Conclusions section.** Per‑gate results whose premises are established findings, each with a premise map (conclusion_id, gate, premises: [proposition_ids], inference: statement + rule_applied, conclusion: assessment). No orphan conclusions; no premise whose status is a work state. **UNRESOLVED may not appear as a terminal analytical conclusion.** Three outcomes only: more work → work layer; all work exhausted → exclude proposition; supported evidence → analytical conclusion permitted.
8. **Mandatory: Operational Audit section.** Every unestablished proposition: proposition_id, work state, avenue dispositions (COMPLETE / BLOCKED / NOT_APPLICABLE + rule_id), barrier_type, remaining_evidentiary_barrier. The reproducible query log = the full escalation ladder (all avenue records, in priority order). **Allowed language:** "Commercial adoption could not be established from the completed evidence protocol." **Prohibited language** (and semantic equivalents) in factual findings: "Not found," "No X was identified," "No evidence of X exists," "appears absent," "there is no evidence that…," "apparently none," "likely not," "could not locate," "no known," "none identified," "no record was found," "Inferred," "Medium completeness."
9. **Mandatory: Decision Matrix output.** Include the state machine result from Phase 5, showing the path taken (anticipation gate → obviousness analysis → motivation object → expected‑success gate → causal bridge test → mechanism/design‑choice distance gates → technical effect → evidence sufficiency gate → finding or work queue). For obviousness, include the Causal Bridge Test (with bridge_status TRAVERSED / UNTRAVERSED) and the structured obviousness evidence object.
10. **Historical patent‑status normalization.** For historical patents, use "Historical term expired: [date] (17 years from grant, subject to the historical patent regime)" rather than modern labels like "Expired — Lifetime."
11. **Forward‑citation labeling.** Low forward‑citation counts are a neutral historical technology‑development signal, not a patentability signal. Do not present them as evidence for or against obviousness.
12. Add appendices: patentability primer, search methodology, **full query log** (every avenue record, per phase, with database and date), original submission record.
13. Run the quality checklist below before delivery.
14. Deliver in the requested format, matched in tone and depth to the audience (inventor vs. TTO vs. investor vs. outside counsel).
15. Return a delivery manifest containing the absolute paths of the compiled report, submission record, proposition ledger, avenue ledger, scores manifest, and rendered HTML/PDF. Verify each path exists and has non‑zero size.

## Quality Checklist (all must pass before delivery)
- [ ] Every quantitative claim is sourced — or the proposition is excluded from factual findings and recorded in the Operational Audit. No unsourced revenue or CAGR figures.
- [ ] Chronology validator passed: all dates consistent, no "before [wrong date]" phrasing.
- [ ] Every legal‑adjacent statement (patentability, FTO‑adjacent, regulatory) carries a "not legal advice" disclaimer.
- [ ] The novelty section explicitly states it is not an FTO opinion if any FTO‑adjacent question was raised anywhere in the engagement.
- [ ] The query log (avenue records) is complete enough that a reviewer could re‑run any search and reproduce the result set.
- [ ] Every unestablished proposition from upstream phases is carried into the Operational Audit rather than silently dropped.
- [ ] Established Findings contains only CONFIRMED PRESENT / CONFIRMED ABSENT rows, each with full provenance; CONFIRMED ABSENT rows carry absence_basis.
- [ ] Every Analytical Conclusion carries a premise map whose premises are established findings; no premise is a work state.
- [ ] No legacy evidence states (NOT OBSERVED / NOT IDENTIFIED / INFERRED / NOT EVALUATED / CONTESTED / UNRESOLVED) appear as active semantics anywhere in the report.
- [ ] No prohibited negative language ("not found," "no evidence of X exists," "none identified," etc.) appears outside the Operational Audit.
- [ ] Commercial readiness is stated as "NOT ESTABLISHED" unless adoption evidence passes the Sufficiency Gate.
- [ ] Decision matrix output is included, showing the reasoning path, and if obviousness was assessed, the Causal Bridge Test (with bridge_status TRAVERSED/UNTRAVERSED) and the structured obviousness evidence object are provided.
- [ ] Conclusion is multidimensional (per‑gate table), not a single compressed patentability label; **no scalar "overall patentability" label appears in the default conclusion output** (an executive score appears only if explicitly requested, labeled as a derived executive summary).
- [ ] Executive Summary ⊆ Established Findings + Analytical Conclusions.
- [ ] No exclusivity framing ("only partner," "no other pathway") survives without an assumption audit.
- [ ] Claim‑construction layer (if used) is clearly labeled as "provisional evaluation claim — not a legal claim construction."

## v1.7 Graph Compilation Contract

Compile conclusions from evidence‑graph artifacts, not from free‑form section text. Every score and recommendation must expose confidence, basis proposition IDs, blockers, evidence debt, and next recovery action. The compiler must propagate upstream constraints and must not upgrade `ESCALATION_REQUIRED`, `BLOCKED`, or `UNRESOLVED — SEARCH‑INCOMPLETE` into a positive conclusion.

## Boundary
- Compiles only — generates no new analysis.
- Depth and tone match the stated audience; do not default to maximal formality if the audience is the inventor themselves.

---

# Phase 9: Render Report

## When to Use
- End of every evaluation run — after Phase 8 has produced the report MD.
- "Generate the branded/PDF report." / "I want the final styled deliverable."

## When NOT to Use
- The report MD doesn't exist yet — run Phase 8 first; never render an unfinished report.

## Execution

**Governing principle:** The renderer is a presentation layer only. It must never invent metrics, findings, or evidence. Every gauge/bar/chart value comes from the per‑run scores manifest, and each score must carry a `basis` proposition_id from the proposition ledger. Charts whose data was not established render labeled placeholder frames — never fabricated series.

1. Confirm the inputs exist:
   - compiled report MD (Phase 8 output, e.g. `report-<id>-e2e-v16.md`)
   - avenue ledger MD (`avenue-ledger-<id>-v16.md`)
   - scores manifest JSON (`scores-<id>.json`)
   - submission record MD (Appendix C, optional but recommended)
   - resolved run directory from the artifact‑destination gate; rendering to a temporary directory or only returning HTML in chat does not satisfy delivery.
2. Run the renderer:
   ```bash
   python3 invention-evaluation-engine/report-renderer/render_report.py \
       --report  evaluations/<id>/report-<id>-e2e-v16.md \
       --ledger  evaluations/<id>/avenue-ledger-<id>-v16.md \
       --scores  evaluations/<id>/scores-<id>.json \
       --submission evaluations/<id>/submission-<id>.md \
       --out evaluations/<id>/report-<id>-e2e-v16.html \
       --pdf
   ```
   `--pdf` triggers the two‑pass render: pass 1 embeds invisible `TOCMARK:<sid>` markers and prints to PDF; the renderer scans the printed PDF with `pdftotext` to learn each section's real physical page; pass 2 fills the TOC page numbers and prints the final PDF with markers stripped.
3. Verify the output (mandatory, do not skip). Every item below must be checked programmatically — "spot‑check a few pages" is not sufficient; the bugs this checklist exists to catch (see "Known failure modes") are systematic and hit every page identically, so a script check on all pages is cheap and a manual spot‑check on a few pages will reliably miss them:
   - `pdfinfo report-<id>-e2e-v16.pdf` → A4 (≈595×842 pts).
   - **Footer regex, every page, no exceptions:** run `pdftotext -f <n> -l <n>` for every physical page and assert the footer line matches `^IEAUS \d[\d,]*: .+\. Submitted \d{4}-\d{2}-\d{2}\. Report \d{4}-\d{2}-\d{2}\.$` exactly (submitted/report dates as clean 10‑character ISO strings, no stray digits spliced in) followed by `Page <n>` as a separate token. If any page's footer date string is not exactly 10 characters, or contains a digit that doesn't belong to the ISO date, the two footer margin boxes are colliding — see Known failure modes #1.
   - **Watermark regex, every page:** assert the extracted watermark text is exactly `CONFIDENTIAL` (13 characters) on every page, not a truncated variant. A watermark missing its first and/or last character indicates a clipping ancestor — see Known failure modes #2.
   - TOC page numbers equal the physical pages where each section divider actually lands (verify against the printed PDF for every TOC entry, not a sample).
   - No `TOCMARK` strings remain in the final PDF or HTML (`pdftotext ... | grep -c TOCMARK` → 0).
   - Gauge/bar labels match the scores manifest tier labels; placeholder frames appear only where the manifest has no data.
   - **Gauge text layer:** gauge scale endpoints are horizontal text runs (`Very Limited` / `Strong`); do not rotate per‑tier labels onto an arc — rotated SVG text scrambles in `pdftotext` extraction and breaks the gauge‑labels verification.
   - **Chart geometry:** for every `<svg>` containing more than one independent data series (e.g. two pie charts), confirm each series has its own `<svg>`/ viewBox rather than sharing coordinate space with another series. Compute each series' painted bounding box and confirm no two series' boxes overlap. Two unrelated pies packed into one viewBox will clip each other's labels — see Known failure modes #4.
- **Cover fits on exactly one page:** the cover must not spill onto page 2. Assert page 2 starts with the first TOC/section content (e.g. `TABLE OF CONTENTS` or `EXECUTIVE SUMMARY`), and assert the disclaimer/legal block's lowest text baseline sits above the footer band (≈y781pt on A4). The cover wordmark and the metadata block occupy separate vertical bands, so no wordmark‑length‑dependent collision is possible — see Known failure modes #3.
4. Deliverables: the styled HTML and the A4 PDF are the final report. Archive both in `evaluations/<id>/`. Return their absolute paths and verify both files exist and are non‑empty before claiming the run is complete.

## Known Failure Modes (Regression List — Check These Explicitly, They Recur)

These four bugs were found together in one production render (v16, US5850650) and all four are systemic — they reproduce on every page or every instance of the pattern, not intermittently, and a checklist that says "verify" without saying *how* will pass a broken render:

1. **Footer margin‑box collision.** The CSS `@page { @bottom-left {...} @bottom-right {...} }` boxes share the page's content width. If `@bottom-left`'s `max-width` leaves less than ~0.5in clearance for `@bottom-right`'s page number, the two boxes' painted text collides, and `pdftotext` (reading by physical glyph position) linearizes the overlap by splicing the page‑number digit into the middle of the date string (`2026-08-14` → `2026-08-114`). Fix: keep `@bottom-left` `max-width` at least ~1in short of the page content width, and give `@bottom-right` explicit `white-space:nowrap` plus a label (`"Page " counter(page)`) so a collision is visually obvious even if the regex check is skipped.
2. **Watermark clipped by an ancestor's `overflow-x:clip`/`hidden`.** A `position:fixed` decorative element (the CONFIDENTIAL watermark) is centered via `top:50%;left:50%;transform:translate(-50%,-50%) rotate(...)`. Its *unrotated* footprint (inflated by large `letter-spacing` at a large `font-size`) can exceed the page's content width even though the rotated visual footprint looks fine. If any ancestor between it and the page root has `overflow-x:clip` or `overflow:hidden`, both edges get clipped symmetrically — dropping the first and last character on every single page (`CONFIDENTIAL` → `ONFIDENTIA`). Fix: scope any horizontal overflow‑clipping to the page *content* wrapper only, never to `html`/`body`, since fixed‑position chrome (the watermark) is a descendant of `body` and inherits that clip. Keep the watermark's raw text run comfortably narrower than the page anyway, as a second line of defense.
3. **Cover vertical overflow.** Cover content (metadata block, legal text, disclaimer) that runs too deep pushes the disclaimer onto page 2, turning a one‑page cover into a two‑page one and offsetting every TOC page number. Fix: keep the cover's vertical rhythm compact — metadata block at ≈4.75in from the page top (16pt rows, slim margins), legal + disclaimer as plain compact text (no box) ending above the footer band (≈y781pt on A4). Verify page 2 begins with TOC/section content, never cover content.
4. **Two data series sharing one SVG viewBox.** A second, smaller pie chart (e.g. a competitive sub‑breakdown) drawn inside the same `<svg>` as an unrelated larger pie chart, positioned in a corner "to save space," will clip whichever labels of the first chart fall in that corner. Two distinct questions (e.g. "top assignees across the whole class" vs. "share among framing‑hammer‑specific brands") are also usually different, non‑additive denominators and should not be visually implied to be one chart's subset. Fix: give each independent series its own `chart-frame`/`<svg>`, sized to the page's normal chart width, not squeezed into a corner of another chart.

## Typographic Reference (Sample‑Faithful Scale)

The branded template reproduces the reference sample's typography:
- Section headings: ~28pt display font, bold, left‑aligned, no forced uppercase (render the report's own heading case; strip any auto number prefix).
- Sub‑headings: ~15pt; body text: ~11.5pt; tables: ~10.5pt.
- TOC entries: ~12pt with dotted leaders and right‑aligned page numbers.
- Cover metadata: ~16‑18pt, rows ~22pt apart, block starting ≈y540 on A4.
- Cover legal + demo disclaimer: small plain text (~7pt), no box, ending above the footer band.

## Quality Checklist (All Must Pass Before Delivery)
- [ ] PDF is A4 with correct physical page numbers in the footer on every page (cover = 1).
- [ ] Footer date strings are clean 10‑character ISO dates on every page — no digits spliced in from the page‑number box (Known failure mode #1).
- [ ] Watermark reads exactly "CONFIDENTIAL" (not truncated) on every page (Known failure mode #2).
- [ ] Cover fits on exactly one page — page 2 begins with TOC/section content, and cover content (metadata, legal, disclaimer) ends above the footer band (Known failure mode #3).
- [ ] Every multi‑series chart uses one `<svg>`/viewBox per series; no two series' bounding boxes overlap (Known failure mode #4).
- [ ] TOC page numbers match actual section pages (verified against the printed PDF for every entry, not guessed).
- [ ] No renderer‑invented metrics: every displayed score exists in the scores manifest with a basis proposition_id.
- [ ] Charts with unestablished data show labeled placeholder frames, never fabricated series.
- [ ] No TOCMARK artifacts in the final HTML/PDF.
- [ ] No legacy evidence states (NOT OBSERVED / INFERRED / UNRESOLVED / NOT IDENTIFIED / CONTESTED) introduced in rendering.
- [ ] The report carries the "not legal advice" disclaimer from the compiled report.

## Landscape & Market Data Integrity Gate

Before delivery, compare every CPC/NAICS code appearing in the rendered Landscape & Market Data section with the classification recorded on the patent front page and in Appendix C. Any mismatch blocks delivery. A placeholder is valid only when the avenue ledger shows the exact query, source, result count, and rejection reason for an attempted pull; an unattempted subsection is a pipeline defect. The renderer must never contain a domain‑specific fallback number or classification.

## Boundary
- Formats only — generates no new analysis, no new scores, no new findings.
- If a scores manifest value is missing, the renderer falls back to a labeled placeholder; do not hand‑edit the HTML to add numbers that are not in the manifest.
- Layout/CSS fixes (footer spacing, clip scoping, chart placement) are presentation‑layer and are fair game to hand‑edit or patch in `render_report.py`'s template — that's different from hand‑editing in a *number* that isn't in the manifest.
```