# Glossary

| Term | Definition |
|---|---|
| **Anticipation** | A single prior-art reference discloses every element (limitation) of a claim. |
| **Obviousness / inventive step** | Whether the claimed subject matter, considered against the relevant prior art and the knowledge or abilities of a skilled person at the relevant date, would have been an obvious modification, combination, substitution, or optimization rather than a non-obvious technical advance. This is not limited to two-reference combinations; a single reference can support an obviousness argument where the difference would have been an obvious modification. **An obviousness finding requires (1) a stated motivation grounded in evidence, not assertion, (2) a reasonable expectation of success consistent with the technical constraints, (3) an assessment of mechanism distance (C0–C4) and design-choice distance (D0–D4) between the claimed mechanism and the closest prior-art mechanism, and (4) a Causal Bridge Test stating what exactly must be invented between the prior art and the claim. Absence of any of these means the obviousness finding is unresolved, not established.** |
| **Combination-obviousness exposure** | The risk that a claim whose novelty rests on combining known elements is nonetheless obvious. **A combination can be completely novel while still being obvious** — novelty and obviousness are different questions. The operative test is *derivation risk*: how readily can the claimed combination be reconstructed from the prior-art components, with a demonstrated motivation to combine them? This replaces the misleading label "combination novelty," which conflated novelty with patentability strength. |
| **Mechanism displacement** | How far the claimed invention moves the *causal intervention point* relative to the closest prior art. Example: prior art controls phase at the electrical-circuit level (different self-induction in circuits); the claim controls phase at the magnetic-material level (saturation-timed shielding). The intervention point moves from the electrical circuit into the magnetic material system — high displacement. High displacement is an argument against obviousness; it must be stated separately from mere "different mechanism" claims and scored explicitly (low / medium / high). |
| **Mechanism distance (C0–C4)** | How far the claimed *physical causal mechanism* moves from the reference mechanism. **Distinct from semantic/structural distance**: two references can be semantically extremely close (same objective, same architecture) yet causally far apart (different physical principle producing the effect). Mechanism distance feeds the inventive-step model; semantic similarity alone must never be read as anticipation or obviousness. Scale: C0 mechanistically identical · C1 essentially the same mechanism with a minor physical variation · C2 same underlying physical principle, different intervention point/configuration · C3 different physical mechanism producing substantially the same effect · C4 fundamentally different causal mechanism / no meaningful shared causal machinery. |
| **Design-choice distance (D0–D4)** | How much conceptual/design selection is required to get from what was known to what was claimed. Defined around the *decision required*, not around novelty. Scale: D0 direct/default choice · D1 routine alternative · D2 non-default selection with a design path visible in prior art · D3 cross-domain/application leap (recognizing a known principle/component can perform a different function, or transferring known machinery to a materially different intervention point, without direct teaching of that move) · D4 unsignposted inventive bridge (new insight; no credible path or expectation of success). **D3 is a diagnostic, not an obviousness verdict** — it describes the bridge; the motivation and expectation gates determine whether the bridge was reasonably traversable. C and D are mandatory, reference-relative, orthogonal fields in every obviousness evidence object; **never mathematically combined** (no C2+D3=5, no weighted average); reported per reference pathway as `C2 / D3`. |
| **Motivation gate** | The requirement that any proposed modification path state *why* a skilled person would have made this particular change, grounded in evidence (a reference, a documented industry problem, an identified technical constraint) — not merely asserted because the change is "plausible." An ungrounded motivation is not established: the motivation proposition enters the work layer until direct or analogous evidence is found or avenues are exhausted. In v1.6 the motivation gate is a **first-class evidence object** (see Motivation Object below) with categorized source lists and a deterministic status derivation. |
| **Search coverage** | Metadata about the evidentiary search behind a negative search result: scope, temporal scope, source domains, search depth, and known limitations. **Coverage is metadata, not evidence.** In v1.6, negative search results are recorded as avenue metadata in the avenue checklist (see Search Escalation Protocol below); coverage objects are replaced by avenue records. Search completion is not evidence — `EXHAUSTED ≠ CONFIRMED ABSENT`. |
| **Knowledge decomposition** | The evidence-stated separation of *known component* ≠ *known function* ≠ *known combination* ≠ *known application*. Each flag carries an evidence state + source (e.g., `component_known: CONFIRMED PRESENT (US424036)`; `application_known: NOT ESTABLISHED (avenue record)`). Lives in the Causal Bridge Test as its `prior_state`; the obviousness evidence object references it. Prevents "X was known" from silently becoming "therefore the application was obvious." |
| **Freedom to Operate (FTO)** | A search for *in-force* patents the invention might infringe. Distinct from a novelty/patentability search: different scope (broader claims, current legal status by jurisdiction), different purpose (commercial risk, not patentability), and requires a formal infringement opinion from counsel. Never substitute a novelty search's output for FTO. |
| **Claim construction** | The process of interpreting the scope and meaning of patent claim language. For evaluation purposes, this involves identifying each limitation (element) of the claim to be mapped against prior art. |
| **Abstract triage** | Fast (30–90 second) screening pass: title → abstract → keywords → classification (Irrelevant / Background / Related / Highly relevant / Potentially blocking). |
| **Claim-element mapping** | The process of taking a target claim, breaking it into individual limitations, and checking each against a prior-art reference's disclosure. A single reference disclosing all limitations = anticipation candidate. |
| **Priority date** | Earliest effective filing date for a patent family. |
| **Patent family** | All filings derived from the same priority application, across jurisdictions. |
| **Legal status** | Active / pending / granted / expired / abandoned — must be checked per jurisdiction, not assumed from one filing. **For historical patents, do not import modern legal-status labels unexamined. Distinguish: patent grant → historical term under applicable law → expiration. Prefer "Historical term expired: [date] (17 years from grant, subject to the historical patent regime)" over "Expired — Lifetime," which imports modern assumptions.** |
| **On-sale bar / public disclosure** | A prior sale offer or public disclosure that starts a statutory filing-deadline clock in most jurisdictions; capture the date, don't just note that disclosure occurred. |
| **Commercial actionability** | Whether a technology has a clear buyer, feasible production cost, an accessible regulatory pathway, and a viable competitive position — distinct from being merely technically interesting. |
| **Counterfactual exclusivity** | An assertion that only one pathway/partner/mechanism exists ("only partner," "no other pathway," "without X, impossible"). **Any such statement triggers an assumption audit**: it claims knowledge of the absence of alternatives, which is almost always beyond the evidence. Replace with "strongest identified pathway" formulations unless absence of alternatives is itself evidenced. |
| **Design-space position** | The region of the inventor's design space that an invention occupies. Same-inventor sibling filings (same higher-level architecture, different physical implementations) indicate a design-space *exploration event* rather than an isolated invention. The evaluator should ask not only "is this patent novel?" but "what region of the inventor's design space does this invention occupy?" |
| **IPC / CPC** | International / Cooperative Patent Classification — structured taxonomy for subject-based (not just keyword) patent searching. |
| **NAICS** | North American Industry Classification System. |
| **CAGR** | Compound Annual Growth Rate. |
| **510(k) / PMA / CE Mark** | US premarket-notification, US premarket-approval, and EU conformity regulatory pathways, respectively. |

---

## Epistemic Architecture — Three Layers

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

**Governing invariant:** Work-state transitions cannot create evidence. Evidence can only be created by verified source support.

### Evidence layer (what the admissible record establishes about the proposition)

| State | Definition | Output Rule |
|---|---|---|
| **CONFIRMED PRESENT** | Directly verified in an admissible source with exact source identity, location/citation, and proposition-level support | Write "Confirmed present in [source]" with source_identity + locator |
| **CONFIRMED ABSENT** | Specifically tested and absent within a defined, bounded evidence universe whose sufficiency requirements have been satisfied | Write "Confirmed absent from [bounded universe definition]" — the finding object MUST carry absence_basis (bounded_universe_definition, sufficiency_test) |

**CONFIRMED ABSENT cannot be produced merely because all search avenues were exhausted.** It requires affirmative absence verification within the declared bounded universe:

```text
EXHAUSTED + no evidence found ≠ CONFIRMED ABSENT

bounded universe defined
+ universe sufficiently covered
+ specific absence tested
+ absence independently verified where schema requires
= CONFIRMED ABSENT
```

### Work layer (what the evaluator is doing)

| State | Level | Definition |
|---|---|---|
| **NOT_STARTED** | engine-internal | Workflow initialization; search has not begun. Never exposed in reports. |
| **SEARCHING** | proposition | Initial search in progress. |
| **ESCALATING** | proposition | Current channel exhausted; moving to the next required avenue. |
| **REQUIRES VERIFICATION** | proposition | Evidence or a source has been located, but its authenticity, provenance, completeness, interpretation, or conflict status has not yet been resolved. Flow: SOURCE LOCATED → REQUIRES VERIFICATION → validated → PRESENT / contradicted → reconcile conflict / unusable → escalate or exclude. |
| **BLOCKED** | avenue | The specified avenue cannot be executed, and the reasonable alternate access routes defined for that avenue have been attempted and failed. Other avenues may remain available. |
| **EXHAUSTED** | proposition | All required avenues have been executed, logged, and dispositioned, and evidence is still insufficient. Never evidence. Never authorizes a factual conclusion. |

### Analytical layer

Evidence → inference → conclusion. Inference is a labeled analytical step, never an evidence state. The Evidence → Inference → Conclusion firewall persists.

### Hard anti-collapse invariants

- `EXHAUSTED ≠ CONFIRMED ABSENT`
- `BLOCKED ≠ CONFIRMED ABSENT`
- `REQUIRES VERIFICATION ≠ CONFIRMED PRESENT`
- `INFERENCE ≠ EVIDENCE`
- **Search completion is not evidence.**

### Legacy-state mapping (v1.5 → v1.6)

<!-- v1.6-legacy-mapping -->
| v1.5 | v1.6 disposition |
|---|---|
| CONFIRMED PRESENT | Evidence state |
| CONFIRMED ABSENT | Evidence state, bounded + sufficient |
| NOT OBSERVED | Avenue/search metadata |
| NOT IDENTIFIED | Avenue/search metadata |
| INFERRED | Analytical inference |
| NOT EVALUATED | Work state (NOT_STARTED → SEARCHING) |
| CONTESTED | Verification/reconciliation work state |
<!-- /v1.6-legacy-mapping -->

---

## Evidence Sufficiency Gate

The gate is the ONLY path by which a proposition becomes a finding. Runs per proposition, per skill:

```text
PROPOSITION
   ↓
1. Required evidence type identified (schema selected from the Proposition-Schema Registry)
   ↓
2. Source acquired
   ↓
3. Source verified (authenticity, provenance, completeness, interpretation)
   ↓
4. Direct proposition support established:
   the source explicitly supports the EXACT proposition asserted,
   not merely a related topic, component, product, or principle
   ↓
5. Independent corroboration where required (schema-driven)
   ↓
6. Scope / proposition-identity check:
   proposition correctly scoped to entity, jurisdiction,
   technology, claim, date (per schema's required_fields)
   ↓
7. Temporal relevance verified (pre-filing / in-period)
   ↓
8. Contradictory evidence checked and reconciled
   ↓
EVIDENCE SUFFICIENT?
   ├── YES → CONFIRMED PRESENT / CONFIRMED ABSENT → finding enters report
   └── NO  → SEARCH ESCALATION
```

Steps 4 and 6 together form the **proposition-identity firewall**: the source must support the exact proposition, and the proposition must be scoped correctly. "Spray cooling was used in military electronics" does not establish "US7216695 Claim 1 was commercially deployed."

**Atomic admission:** proposition admission is all-or-nothing. If one mandatory field is missing, the proposition fails sufficiency. "Mostly supported" is not a state.

**Corroboration (schema-driven):**

```yaml
corroboration:
  required: true
  minimum_independent_sources: 2
  source_independence_rule: MATERIAL_PROVENANCE_INDEPENDENCE
```

- **Independent source** = materially independent provenance. Republished, syndicated, scraped, mirrored, press-release-derived, or citation-chain-dependent copies of the same underlying evidence count as one source.
- **Lineage is an auditable field, not only a rule.** Every source carries an `independence_lineage_id`; sources sharing a lineage ID count as one source for corroboration. Three documents on lineage `L-0007` = one evidence lineage; two genuinely independent sources carry `L-0007` and `L-0012`.
- `minimum_independent_sources` is per-schema: patent grant date may need 1 primary record; commercial adoption needs 2 independent product-identity links; historical absence needs a bounded universe + 2 independent records.
- Single-source support yields at most `CONFIRMED PRESENT` with a single-source caveat — never `CONFIRMED ABSENT`.

**Contradiction handling:** contradictory evidence → `REQUIRES VERIFICATION` → reconcile; if irreconcilable, the proposition is excluded (unestablished), never reported as contested.

---

## Proposition-Schema Registry

Single authoritative registry. Skills reference schema IDs; no schema may be duplicated, modified, or extended in a skill file. Schema drift between skills and the compiler is forbidden.

```yaml
schema_id: market_relevance_award
version: 1
required_fields:
  - agency
  - award_id
  - recipient
  - award_date
  - title
  - url
  - relevant_passage
  - independence_lineage_id
corroboration:
  required: true
  minimum_independent_sources: 2
```

| schema_id | version | Skills | required_fields (exact identifiers) | corroboration |
|---|---|---|---|---|
| `prior_art_disclosure` | 1 | 04, 05 | patent/publication ID, jurisdiction, date, relevant passage, claim-element mapping | required: false |
| `literature_disclosure` | 1 | 06 | authors, title, venue, date, DOI/report no., URL, experimental system, technology, application, demonstrated result, relevance | required: false |
| `market_relevance_award` | 1 | 07 | agency, award_id, recipient, award_date, title, url, relevant_passage, independence_lineage_id | required: true, min 2 |
| `market_relevance_report` | 1 | 07 | publisher, report_id, title, date, url, relevant_passage, independence_lineage_id | required: true, min 2 |
| `market_sizing` | 1 | 07 | market_boundary, geography, time_period, figure, source, reconciliation, derivation | required: true, min 2 |
| `naics_classification` | 1 | 07 | taxonomy_source, code, official_title, edition_year, basis | required: false |
| `commercial_adoption` | 1 | 07 | product_identity_link, source, date, independence_lineage_id | required: true, min 2 |
| `regulatory_regime` | 1 | 03 | governing_statute, inside_outside_basis | required: false |
| `partner_fit` | 1 | 08 | sells, buys, technical_need, invention_mapping | required: false |
| `performance_data` | 1 | 03, 05 | metric, value, test_conditions, source, date | required: false |

**Row non-existence rule:** a finding row does not exist unless every required schema field is populated with an exact identifier. "Various SBIR awards…" fails `market_relevance_award` (no award_id). "NAICS 334419 – INFERRED" fails `naics_classification` (no taxonomy_source, no edition_year, no basis). "Research on UAV spray cooling…" fails `literature_disclosure` (no publication identity, no demonstrated result).

---

## Search Escalation Protocol

**BLOCKED is an avenue disposition. EXHAUSTED is a proposition-level termination state.** A blocked avenue does not imply the proposition is excluded; other avenues can still complete.

### Avenue checklists (deterministic priority)

Each search skill defines its mandatory avenues with fixed priority ordering — same proposition + same skill + same avenue configuration → same escalation ladder. The model cannot skip avenues mid-run.

**Default avenue template:**

```yaml
search_escalation:
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
```

Each avenue carries an audit record:

```yaml
avenue_record:
  id: A1
  name: primary_source_search
  priority: 1
  status: COMPLETE | BLOCKED | NOT_APPLICABLE | REQUIRES_VERIFICATION
  record:
    searches_run: []
    sources_consulted: []
    relevant_results: []
    exclusions: []
    limitations: []
    completion_basis: ""
```

### Avenue status semantics

- **COMPLETE** — the specified avenue was actually searched with the required query family, results screened, action logged. Not "I checked another database."
- **BLOCKED** — the specified avenue cannot be executed, and the reasonable alternate access routes defined for that avenue have been attempted and failed.
- **NOT_APPLICABLE** — requires a machine-checkable rule, never model preference:
  ```yaml
  status: NOT_APPLICABLE
  rule_id: "NA-07"
  rule_basis: "Proposition is jurisdiction-neutral; jurisdiction-specific search would not add evidentiary value."
  ```
- **REQUIRES_VERIFICATION** — the avenue returned evidence that exists but cannot yet be trusted or reconciled (e.g., two dates disagree). The proposition remains in the work layer until verification resolves it.

### Termination state machine

```text
PROPOSITION
   ↓
EVIDENCE SUFFICIENT? ──YES──→ CONFIRMED PRESENT / ABSENT → STOP
   ↓ NO
ESCALATE → next required avenue (by priority) → search + log → EVIDENCE SUFFICIENT?
   ├── YES → STOP
   └── NO → next avenue
              ↓
        all required avenues dispositioned?
           ├── NO → continue
           └── YES → EXHAUSTED (proposition-level) → STOP
```

### Hard invariants

1. `EXHAUSTED` may be emitted only when every required avenue is in `COMPLETE`, `BLOCKED`, or `NOT_APPLICABLE`. **No required avenue may remain `REQUIRES_VERIFICATION`.**
2. `EXHAUSTED` never constitutes evidence and never authorizes a factual conclusion.
3. Supplemental avenues are allowed only as explicit logged exceptions — never part of termination logic.
4. Search completion is not evidence (`EXHAUSTED ≠ CONFIRMED ABSENT`).

### Post-EXHAUSTED disposition

The proposition is omitted from factual findings and retained only in the operational audit as an unestablished proposition, with `barrier_type` and `remaining_evidentiary_barrier`.

---

## Finding Object & Proposition Identity

Every finding is a structured object that must fully validate against its schema:

```yaml
finding:
  proposition_id: P-07-003
  proposition_version: 1
  proposition: "exact proposition text"
  proposition_scope:
    required_fields: [entity, technology_identity, temporal_window]
    entity: ""
    jurisdiction: ""            # mandatory only if schema declares it
    technology_identity: ""
    claim_reference: ""         # mandatory only if schema declares it
    temporal_window: ""
  evidence_schema: market_relevance_award
  corroboration:
    required: true
    minimum_independent_sources: 2
    source_independence_rule: MATERIAL_PROVENANCE_INDEPENDENCE
  evidence:
    - source_identity:
        source_type: "SBIR award"
        publisher_or_issuer: ""
        title_or_identifier: ""
        publication_or_issue_date: ""
        persistent_identifier: ""   # patent number, DOI, award ID, report number
        locator: ""                 # URL, page, claim, section, passage
      award_id: ""
      recipient: ""
      award_date: ""
      award_amount: ""
      relevant_passage: ""
      independence_lineage_id: L-0007
      independence_lineage: "primary record"   # vs. "derived from [primary]"
  relationship:
    technology_relationship: DIRECT | RELATED | GENERAL
    relevance_explanation: ""
  conclusion:
    evidence_state: CONFIRMED PRESENT | CONFIRMED ABSENT
    basis: ""
  absence_basis:                  # REQUIRED when evidence_state: CONFIRMED ABSENT
    bounded_universe_definition: ""
    sufficiency_test: ""
```

**Rules:**
- **Row non-existence:** if any mandatory schema field is empty, the finding object does not exist — there is nothing to report.
- **Proposition identity:** each proposition carries a stable `proposition_id` + `proposition_version`. The same ID carries the same evidence state across skill hand-offs. **A proposition ID may not change evidence schema, scope, or proposition text without a version increment** (P-07-003 v1 → P-07-003-v2 or a new ID).
- **Source identity:** durable `source_identity` fields beyond URL — the object is defensible even if the URL later changes.
- **Scope fields are schema-specific:** `proposition_scope.required_fields` is declared by the schema; a jurisdiction-neutral proposition is not forced to invent a jurisdiction.
- **Atomic admission:** the gate is all-or-nothing per proposition.

---

## Report Architecture

Three conceptual areas. **Operational Audit cannot flow backward into Established Findings** — a completed search does not become a fact.

### 1. Established Findings
Only rows that passed the Sufficiency Gate (`CONFIRMED PRESENT` / `CONFIRMED ABSENT`), each rendered from its finding object with full provenance.

### 2. Analytical Conclusions
Per-gate results whose premises are established findings. Every analytical conclusion carries a premise map:

```yaml
analytical_conclusion:
  conclusion_id: C-05-002
  gate: obviousness
  premises:
    - proposition_id: P-05-001
    - proposition_id: P-05-004
  inference:
    statement: ""
    rule_applied: ""
  conclusion:
    assessment: ""
```

Hard trace: Conclusion → Premises → Finding objects → Sources. No orphan conclusions. No conclusion may use a premise whose status is a work state (e.g., `EXHAUSTED`) as though it were evidence.

**Provenance by layer:**
```text
Factual assertion
→ source_identity + locator

Analytical conclusion
→ premise_map + inference + rule_applied
```

**UNRESOLVED may not appear as a terminal analytical conclusion.** Three outcomes only: more work → work layer; all work exhausted → exclude proposition; supported evidence → analytical conclusion permitted.

### 3. Operational Audit
Unestablished propositions and search records. Each excluded proposition carries:

```yaml
barrier_type:
  - source_unavailable
  - insufficient_identity
  - insufficient_corroboration
  - unresolved_conflict
  - insufficient_temporal_match
  - scope_mismatch
  - insufficient_technical_demonstration
  - insufficient_search_completion
remaining_evidentiary_barrier: ""
```

The reproducible query log = the full escalation ladder (all avenue records, in priority order).

**Allowed language:** "Commercial adoption could not be established from the completed evidence protocol."

**Prohibited language** (and semantic equivalents) in factual findings: "Not found," "No X was identified," "No evidence of X exists," "appears absent," "there is no evidence that…," "apparently none," "likely not," "could not locate," "no known," "none identified," "no record was found," "Inferred," "Medium completeness." Allowed only in the Operational Audit describing search activity.

### Executive summary
Derived only on request, labeled as derived, and formally constrained:

```text
Executive Summary ⊆ Established Findings + Analytical Conclusions
```

The audit may be referenced ("Several evidentiary gaps remain and are documented in the Operational Audit") but never converted into factual prose.

---

## Evidence → Inference → Conclusion Firewall

**The core architectural rule of this framework:** nothing downstream is allowed to promote an inference into a fact.

Every substantive finding must be decomposed into its three layers, and each layer must be labeled with a strength/confidence that is *consistent with the evidence grade that supports it*. An inference cannot be labeled "strong" if its supporting evidence is unestablished (work state, not evidence). A conclusion cannot be labeled "high confidence" if its inference is weak. **No downstream section may cite an inference as if it were an established fact** — if the report later references a proposition, it must carry the same evidence grade it had when first established.

```yaml
finding:
  proposition: ""
  evidence:
    - source: ""
      observation: ""
  inference:
    statement: ""
    strength: weak | moderate | strong
  conclusion:
    statement: ""
    confidence: low | medium | high
```

Example — the classic failure this firewall prevents:

```yaml
finding:
  proposition: "The shield mechanism was obvious to a skilled person in 1890"

  evidence:
    - source: "US416195"
      observation: "Tesla already used self-induction to create phase differences."

    - source: "historical electromagnetic knowledge"
      observation: "Magnetic saturation was known."

    - source: "search results"
      observation: "No accessible pre-1890 source was identified describing this exact shield mechanism."

  inference:
    statement: "A skilled person could potentially have considered magnetic saturation as another phase-delay mechanism."
    strength: moderate

  conclusion:
    statement: "Obviousness remains plausible but is not established."
    confidence: medium
```

The firewall makes it structurally difficult to collapse the inference into "Therefore obvious."

---

## Relationship Ontology — Multi-Dimensional

### Structural Layer (E0–E5)

| Level | Definition | Example |
|---|---|---|
| **E0** | Unrelated | Different domain entirely |
| **E1** | Same terminology / domain | Same keywords, different mechanism |
| **E2** | Shared components | Same structural elements |
| **E3** | Same functional objective | Solves the same problem |
| **E4** | Same causal architecture | Same problem-solving path |
| **E5** | Same mechanism | Same physical/chemical principle |

**Critical:** E0–E5 describes **structural similarity only**. It is **not a patentability score** and **not a legal conclusion**. E5 does not mean anticipation; E3 does not mean obviousness.

### Mechanism Distance Layer (separate dimension)

| Level | Definition |
|---|---|
| **C0** | Mechanistically identical |
| **C1** | Essentially the same mechanism with a minor physical variation |
| **C2** | Same underlying physical principle, different intervention point/configuration |
| **C3** | Different physical mechanism producing substantially the same effect |
| **C4** | Fundamentally different causal mechanism / no meaningful shared causal machinery |

### Design-Choice Distance Layer (separate dimension, v1.5)

| Level | Definition |
|---|---|
| **D0** | Direct/default choice — natural or routine implementation of the known teaching |
| **D1** | Routine alternative — one of a small number of directly suggested alternatives |
| **D2** | Non-default selection — choosing among several viable alternatives with ordinary trade-offs; path visible in prior art |
| **D3** | Cross-domain/application leap — recognizing a known principle/component can perform a different function, or transferring known machinery to a materially different intervention point, without direct teaching of that move. **Diagnostic, not an obviousness verdict.** |
| **D4** | Unsignposted inventive bridge — requires a new insight, substantial engineering development, or a design move with no credible path or expectation of success |

Semantic similarity (E-layer), mechanism distance (C-layer), and design-choice distance (D-layer) are independent. A reference can be E4 (very close structurally) while being C3 (different physical principle) — that combination is a *strong non-obviousness argument*, and the report must not let the E-layer closeness bleed into the inventive-step conclusion without the C/D-layer assessment. C and D are **never combined into a single score**; both are reported per reference pathway (e.g., `C2 / D3`).

### Legal Layer (separate dimension)

- **Anticipation** — single reference discloses all limitations.
- **Obviousness** — modification/combination/substitution/optimisation would have been obvious, gated on the Motivation Object + expectation-of-success + the Causal Bridge Test + mechanism/design-choice distance.
- **Infringement / FTO** — entirely different question (not evaluated here).

### Evidence Layer (separate dimension)

- **CONFIRMED PRESENT / CONFIRMED ABSENT** (evidence layer) — applies to every factual observation that passed the Evidence Sufficiency Gate. Unestablished propositions carry work states (SEARCHING / ESCALATING / REQUIRES VERIFICATION / EXHAUSTED) and avenue records, not evidence states. A complete record must state all dimensions independently.

---

## Obviousness Evidence Object

When obviousness is analysed, the following structured object must be produced. In v1.5 it is the **audit trail backing the Causal Bridge Test** (below) — the bridge test states *what exactly has to be invented*; this object records *how we know*.

```yaml
obviousness_case:
  closest_reference:
    patent_or_publication: [identifier]
    relevance: [E0–E5 classification]
    mechanism_distance: [C0–C4 from claimed mechanism]
    design_choice_distance: [D0–D4 — cross-domain/application leap is D3]
  knowledge_decomposition:            # ← references the bridge test's prior_state
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
  motivation:                          # ← first-class object (see Motivation Object below)
    direct: [{source, support}]
    analogous: [{source, support}]
    inferred: [{source, support}]
    contradicted: [{source, support}]
    status: [GROUNDED | PARTIALLY GROUNDED | RECONCILIATION REQUIRED]
    work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]
  proposed_modification_paths:
    - type: [modification | combination | substitution | optimization]
      description: [what would be changed]
      prior_art_basis: [reference(s) that teach the change]
      motivation_delta: [only if this path materially differs from the shared motivation object; omit otherwise]
      reasonable_expectation_of_success: [high/medium/low]
      compatibility_constraints: [any technical barriers]
  mechanism_displacement:
    prior_art_control_domain: [e.g., electrical_circuit | circuit_inductance | ...]
    claimed_control_domain: [e.g., magnetic_material | ...]
    displacement: [low | medium | high]
    rationale: [why the intervention point moved]
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
      note: [observations that neither support nor undermine obviousness — e.g., low forward-citation counts are a historical technology-development signal, not a patentability signal]
  unresolved_questions:
    - [any unanswered issues]
  evidence_state: [CONFIRMED PRESENT | CONFIRMED ABSENT]
  final_assessment: [Limited / Moderate / High obviousness risk — with rationale]
```

**Note:** If motivation, expectation-of-success, or the causal bridge cannot be evidenced, the obviousness proposition is not assessed as a conclusion — it is excluded from factual findings and recorded in the Operational Audit with `barrier_type`.

**Known principle ≠ obvious application.** Establish this explicitly: "iron saturates" (background principle, CONFIRMED PRESENT) does not by itself establish "therefore a skilled engineer would choose an insulated iron-wire shield interposed between coil and core as a controllable phase-delay mechanism in an AC motor" (engineering application). The application step must be evidenced independently; if the specific application is not established in the accessible record (avenue record: NOT ESTABLISHED), the application proposition enters the work layer and the confidence of any obviousness finding must be weakened accordingly. The **knowledge decomposition** makes this structural: `principle_known: CONFIRMED PRESENT` coexists with `application_known: NOT ESTABLISHED (avenue record)`.

This object ensures that obviousness analysis is as auditable and structured as the anticipation gate.

---

## Motivation Object (v1.5)

The motivation gate is analyzed once per obviousness evidence object (path-independent), as a first-class object with **categorized source lists, not counts** — counts are gameable; listed sources are auditable.

```yaml
motivation:
  proposition: [the move a skilled person is asserted to have reason to make]
  direct:      - source: [citation]
                 support: [one-line support]
  analogous:   - source: [citation]
                 support: [one-line support]
  inferred:    - source: [citation]
                 support: [one-line support]
  contradicted:- source: [citation]
                 support: [one-line support]
  status: [derived per table below]
```

**Deterministic derivation:**

| Evidence condition | Motivation status |
|---|---|
| ≥1 direct, no unresolved contradiction | **GROUNDED** |
| No direct, ≥1 analogous, no unresolved contradiction | **PARTIALLY GROUNDED** |
| Only inferred | Motivation not established; proposition enters work layer (SEARCHING/ESCALATING) until direct or analogous evidence is found or avenues are exhausted |
| Any contradicted evidence | **RECONCILIATION REQUIRED** |

**Guardrails:** presence of a higher category does not automatically erase contradiction — a direct source plus a serious contradictory source becomes RECONCILIATION REQUIRED until resolved. Multiple analogous sources never accumulate into direct evidence — three analogies are still analogical evidence.

**Key distinction:** motivation asks whether the skilled person had *reason* to make the move; the modification path asks *what move* they would make. A plausible path is not evidence of motivation. `proposed_modification_paths` therefore carry `motivation_delta` only when a path materially differs from the shared motivation object.

---

## Causal Bridge Test (v1.5)

The **mandatory centerpiece** of the obviousness analysis. States what exactly must be invented between the prior art and the claim, and whether the evidence shows a skilled person could reasonably have crossed that bridge.

```yaml
causal_bridge_test:
  prior_state:
    known_objective: [evidence-stated]
    known_components: [evidence-stated]   # ← knowledge decomposition lives here
    known_principles: [evidence-stated]   #   (component/principle/function/combination/application)
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
    post_filing: excluded   # post-filing disclosures never count as pre-filing bridge evidence
  motivation: { ... }                        # ← the first-class Motivation Object
  expectation_of_success:
    technical: [high/medium/low]
  unexpected_result:
    identified: [true/false]
    detail: [if true]
  bridge_status: [TRAVERSED | UNTRAVERSED]
  bridge_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]
```

**bridge_status semantics:**

- **TRAVERSED** — evidence shows a skilled person would cross the bridge (obviousness strengthens).
- **UNTRAVERSED** — evidence shows the bridge was not reasonably crossable (e.g., unexpected result, technical failure, high design-choice distance with no path) — a non-obviousness argument.
- **When motivation or application evidence is insufficient, the bridge is not assessed as a conclusion** — the proposition enters the work layer (bridge_work_state: SEARCHING / ESCALATING / REQUIRES VERIFICATION / EXHAUSTED) until evidence is established or the avenue checklist is exhausted. UNRESOLVED is not a terminal state.

**Central question:** *What exactly has to be invented between the prior art and the claim?* If the required_change is empty (prior art already teaches the full move), that is anticipation territory, not obviousness. If the required_change is a cross-domain/application leap (D3) with no motivation evidence, the bridge proposition enters the work layer regardless of how plausible the path sounds.

---

## Decision Matrix — Novelty Search State Machine

```text
PRIOR ART REFERENCE │
                    ▼
            ┌─────────────────┐
            │ Claim mapping    │
            └────────┬────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ALL LIMITATIONS           ANY LIMITATION
       DISCLOSED?               MISSING?
         │                       │
        YES                     YES
         │                       │
         ▼                       ▼
  ANTICIPATION GATE      OBVIOUSNESS ANALYSIS
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                 Modify        Combine        Substitute
                                                    │
                     ▼
MOTIVATION GATE
                                            (first-class object:
                                             GROUNDED /
                                             PARTIALLY GROUNDED /
                                             RECONCILIATION REQUIRED;
                                             ungrounded motivation
                                             enters the work layer)
                                                      │
                                                      ▼
                                           EXPECTED-SUCCESS GATE
                                                      │
                                                      ▼
                                             CAUSAL BRIDGE TEST
                                             (prior_state →
                                              claimed_state →
                                              required_change →
                                              bridge_evidence →
                                              bridge_status:
                                              TRAVERSED /
                                              UNTRAVERSED;
                                              insufficient evidence →
                                              work layer)
                                                      │
                                                      ▼
                                             MECHANISM-DISTANCE
                                             + DESIGN-CHOICE
                                             DISTANCE GATES
                                             (C0–C4 / D0–D4,
                                              per reference pathway,
                                              never combined)
                                                      │
                                                      ▼
                                              TECHNICAL EFFECT
                                                      │
                                                      ▼
                                              UNEXPECTED RESULT?
                                                      │
                                                      ▼
                                              EVIDENCE FIREWALL
                                              (no inference
                                               promoted to fact)
                                                      │
                                                      ▼
                                              EVIDENCE SUFFICIENCY GATE
                                              → FINDING (CONFIRMED
                                                PRESENT / ABSENT)
                                              or WORK QUEUE
                                                (escalation)
```

---

## Multidimensional Decision Output

Do **not** collapse the pipeline result into a single compressed label such as "MODERATE patentability." "Moderate obviousness risk" ≠ "moderate patentability" — they are not inverses. **The native output is the per-gate result table** (v1.5):

| Gate | Result |
|---|---|
| Utility | Strong / Moderate / Weak |
| Novelty / anticipation | Strongly supported / Supported / Not established |
| Causal distinction from closest prior art | Strong / Moderate / Weak (with C0–C4 / D0–D4 per reference) |
| Obviousness risk | Limited / Moderate / High — or "not established" (proposition excluded, see Operational Audit) |
| Causal Bridge Test status | TRAVERSED / UNTRAVERSED — insufficient evidence → work layer (see Operational Audit) |
| Unexpected-result evidence | Present / Absent / Not established (see Operational Audit) |
| Historical disclosure coverage | Established / Not established (see Operational Audit) |
| Commercial adoption evidence | CONFIRMED PRESENT / CONFIRMED ABSENT / Not established (see Operational Audit) |
| Market sizing | Established / Not established (see Operational Audit) |

**v1.5 rule:** there is **no "Overall patentability" row in the default output.** The per-gate table above is the only conclusion the pipeline produces. An executive score ("Indeterminate-to-[level]") may be derived **only if the user explicitly requests an executive summary score**; when derived it must be labeled as a derived executive summary (not a pipeline output), produced by the report compiler using "Indeterminate-to-[level]" as the derivation rule, and always accompanied by the full per-gate table. Never let an unresolved gate read as a resolved one.
