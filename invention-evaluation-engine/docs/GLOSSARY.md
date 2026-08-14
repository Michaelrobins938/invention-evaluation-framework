# Glossary

| Term | Definition |
|---|---|
| **Anticipation** | A single prior-art reference discloses every element (limitation) of a claim. |
| **Obviousness / inventive step** | Whether the claimed subject matter, considered against the relevant prior art and the knowledge or abilities of a skilled person at the relevant date, would have been an obvious modification, combination, substitution, or optimization rather than a non-obvious technical advance. This is not limited to two-reference combinations; a single reference can support an obviousness argument where the difference would have been an obvious modification. **An obviousness finding requires (1) a stated motivation grounded in evidence, not assertion, (2) a reasonable expectation of success consistent with the technical constraints, (3) an assessment of mechanism distance (C0–C4) and design-choice distance (D0–D4) between the claimed mechanism and the closest prior-art mechanism, and (4) a Causal Bridge Test stating what exactly must be invented between the prior art and the claim. Absence of any of these means the obviousness finding is unresolved, not established.** |
| **Combination-obviousness exposure** | The risk that a claim whose novelty rests on combining known elements is nonetheless obvious. **A combination can be completely novel while still being obvious** — novelty and obviousness are different questions. The operative test is *derivation risk*: how readily can the claimed combination be reconstructed from the prior-art components, with a demonstrated motivation to combine them? This replaces the misleading label "combination novelty," which conflated novelty with patentability strength. |
| **Mechanism displacement** | How far the claimed invention moves the *causal intervention point* relative to the closest prior art. Example: prior art controls phase at the electrical-circuit level (different self-induction in circuits); the claim controls phase at the magnetic-material level (saturation-timed shielding). The intervention point moves from the electrical circuit into the magnetic material system — high displacement. High displacement is an argument against obviousness; it must be stated separately from mere "different mechanism" claims and scored explicitly (low / medium / high). |
| **Mechanism distance (C0–C4)** | How far the claimed *physical causal mechanism* moves from the reference mechanism. **Distinct from semantic/structural distance**: two references can be semantically extremely close (same objective, same architecture) yet causally far apart (different physical principle producing the effect). Mechanism distance feeds the inventive-step model; semantic similarity alone must never be read as anticipation or obviousness. Scale: C0 mechanistically identical · C1 essentially the same mechanism with a minor physical variation · C2 same underlying physical principle, different intervention point/configuration · C3 different physical mechanism producing substantially the same effect · C4 fundamentally different causal mechanism / no meaningful shared causal machinery. |
| **Design-choice distance (D0–D4)** | How much conceptual/design selection is required to get from what was known to what was claimed. Defined around the *decision required*, not around novelty. Scale: D0 direct/default choice · D1 routine alternative · D2 non-default selection with a design path visible in prior art · D3 cross-domain/application leap (recognizing a known principle/component can perform a different function, or transferring known machinery to a materially different intervention point, without direct teaching of that move) · D4 unsignposted inventive bridge (new insight; no credible path or expectation of success). **D3 is a diagnostic, not an obviousness verdict** — it describes the bridge; the motivation and expectation gates determine whether the bridge was reasonably traversable. C and D are mandatory, reference-relative, orthogonal fields in every obviousness evidence object; **never mathematically combined** (no C2+D3=5, no weighted average); reported per reference pathway as `C2 / D3`. |
| **Motivation gate** | The requirement that any proposed modification path state *why* a skilled person would have made this particular change, grounded in evidence (a reference, a documented industry problem, an identified technical constraint) — not merely asserted because the change is "plausible." An ungrounded motivation must be labeled INFERRED and the obviousness finding treated as unresolved. In v1.5 the motivation gate is a **first-class evidence object** (see Motivation Object below) with categorized source lists and a deterministic status derivation. |
| **Search coverage** | Metadata about the evidentiary search behind a negative finding: scope, temporal scope, source domains, search depth, completeness (LOW / MEDIUM / HIGH / EXHAUSTIVE), and known limitations. **Coverage is metadata, not evidence.** It may qualify the reliability of a negative finding and may authorize a targeted re-evaluation, but it MUST NOT automatically change the evidence state. Mandatory on NOT OBSERVED, NOT IDENTIFIED, and CONFIRMED ABSENT. See Negative Evidence Coverage Rule below. |
| **Knowledge decomposition** | The evidence-stated separation of *known component* ≠ *known function* ≠ *known combination* ≠ *known application*. Each flag carries an evidence state + source (e.g., `component_known: CONFIRMED PRESENT (US424036)`; `application_known: NOT OBSERVED (coverage)`). Lives in the Causal Bridge Test as its `prior_state`; the obviousness evidence object references it. Prevents "X was known" from silently becoming "therefore the application was obvious." |
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

## Evidence Status — Global Ontology

| State | Definition | Output Rule |
|---|---|---|
| **CONFIRMED PRESENT** | Directly verified in source | Write "Confirmed present in [source]" with citation |
| **CONFIRMED ABSENT** | Within a defined and sufficiently complete evidence universe, the target was specifically tested for and found absent | Write "Confirmed absent from [bounded universe definition]" — **requires both a coverage object and a bounded search universe** (type, definition, completeness, exclusions). Never assign on LOW/MEDIUM coverage; never assign to an inherently open historical universe unless a bounded record is defined |
| **NOT OBSERVED** | Searched sources contain no observed instance, **but search coverage is insufficient to establish historical absence** | Write "Not observed in [searched sources]; coverage insufficient to establish absence" — **requires a coverage object** |
| **NOT IDENTIFIED** | Searched, not found (a search was performed but returned nothing) | Write "Not identified in [searched sources]" — **requires a coverage object** |
| **NOT EVALUATED** | Search not performed | Write "Not evaluated" |
| **INFERRED** | Derived by reasoning from confirmed evidence; not directly observed | Write "Inferred from [evidence], not directly observed" |
| **CONTESTED** | Sources conflict; no reconciliation possible at this level | Write "Contested: [source A] vs [source B]" |

**Rule:** Never convert "not identified," "not evaluated," or "not observed" into "does not exist." Never conflate "confirmed absent" (bounded universe + sufficient coverage) with "not observed" (coverage-insufficient). These are distinct states with distinct evidentiary weight — **not observed is the default for negative historical claims**, because historical records are almost never dense enough to support confirmed absence.

**Negative Evidence Coverage Rule (v1.5):** Every `NOT OBSERVED`, `NOT IDENTIFIED`, or `CONFIRMED ABSENT` finding MUST carry a structured coverage object documenting search scope, temporal scope, source-domain coverage, search depth, completeness, and known limitations. Coverage is metadata about the evidentiary search, not evidence itself. Coverage may qualify the reliability of a negative finding and may authorize a targeted re-evaluation, but it MUST NOT automatically change the evidence state. `CONFIRMED ABSENT` additionally requires a defined and sufficiently complete evidence universe. Epistemic rule: **you can increase search coverage without increasing certainty — you need new evidence to increase certainty.**

Coverage level semantics:

| Level | Meaning |
|---|---|
| **LOW** | Narrow/partial search. Absence inference is weak. |
| **MEDIUM** | Multiple relevant sources searched, but meaningful gaps remain. |
| **HIGH** | Broad, targeted search across the principal relevant record with documented residual gaps. |
| **EXHAUSTIVE** | Only available where the search domain is demonstrably bounded and substantially complete. |

**Prohibited:** automatic `coverage_level: HIGH → CONFIRMED ABSENT`; `coverage_level: LOW + CONFIRMED ABSENT` at all. Coverage determines whether a state transition is *permissible*; evidence determines whether the transition actually occurs.

**Distinct negative-state semantics:** `NOT OBSERVED` = negative search result (universe incomplete / coverage insufficient) · `NOT IDENTIFIED` = negative identification result (documentary search target) · `CONFIRMED ABSENT` = bounded negative finding (requires coverage AND a bounded universe).

---

## Evidence → Inference → Conclusion Firewall

**The core architectural rule of this framework:** nothing downstream is allowed to promote an inference into a fact.

Every substantive finding must be decomposed into its three layers, and each layer must be labeled with a strength/confidence that is *consistent with the evidence grade that supports it*. An inference cannot be labeled "strong" if its supporting evidence is NOT OBSERVED. A conclusion cannot be labeled "high confidence" if its inference is weak. **No downstream section may cite an inference as if it were an established fact** — if the report later references a proposition, it must carry the same evidence grade it had when first established.

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

- **CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED** — applies to every factual observation. A complete record must state all dimensions independently.

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
    component_known: [CONFIRMED PRESENT (source) | NOT OBSERVED (coverage) | ...]
    principle_known: [CONFIRMED PRESENT (source) | ...]
    function_known: [CONFIRMED PRESENT (source) | ...]
    combination_known: [NOT OBSERVED (coverage) | ...]
    application_known: [NOT OBSERVED (coverage) | ...]
    motivation_to_combine: [GROUNDED | PARTIALLY GROUNDED | INFERRED | RECONCILIATION REQUIRED]
  coverage:                            # mandatory on every negative finding
    scope: [what proposition was searched]
    temporal_scope: [window searched]
    source_domains: [patent records / historical company records / technical literature / ...]
    search_depth: [full / partial]
    completeness: [LOW | MEDIUM | HIGH | EXHAUSTIVE]
    limitations: [documented gaps]
  distinguishing_limitations:
    - limitation: [text]
      disclosed_in_closest: [yes/no]
      delta: [what is different]
  motivation:                          # ← first-class object (see Motivation Object below)
    direct: [{source, support}]
    analogous: [{source, support}]
    inferred: [{source, support}]
    contradicted: [{source, support}]
    status: [GROUNDED | PARTIALLY GROUNDED | INFERRED | RECONCILIATION REQUIRED]
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
    evidence: [CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED]
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
  evidence_state: [CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED]
  final_assessment: [Limited / Moderate / High obviousness risk — or UNRESOLVED when motivation, expectation, or mechanism/design-choice distance cannot be evidenced — with rationale]
```

**Known principle ≠ obvious application.** Establish this explicitly: "iron saturates" (background principle, CONFIRMED PRESENT) does not by itself establish "therefore a skilled engineer would choose an insulated iron-wire shield interposed between coil and core as a controllable phase-delay mechanism in an AC motor" (engineering application). The application step must be evidenced independently; if the specific application is NOT OBSERVED / NOT IDENTIFIED in the accessible record, the confidence of any obviousness finding must be weakened accordingly. The **knowledge decomposition** makes this structural: `principle_known: CONFIRMED PRESENT` coexists with `application_known: NOT OBSERVED`.

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
| Only inferred | **INFERRED** |
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
  bridge_status: [TRAVERSED | UNTRAVERSED | UNRESOLVED]
```

**bridge_status semantics:**

- **TRAVERSED** — evidence shows a skilled person would cross the bridge (obviousness strengthens).
- **UNTRAVERSED** — evidence shows the bridge was not reasonably crossable (e.g., unexpected result, technical failure, high design-choice distance with no path) — a non-obviousness argument.
- **UNRESOLVED** — neither direction is evidenced. **The default when motivation is INFERRED or application is NOT OBSERVED.**

**Central question:** *What exactly has to be invented between the prior art and the claim?* If the required_change is empty (prior art already teaches the full move), that is anticipation territory, not obviousness. If the required_change is a cross-domain/application leap (D3) with no motivation evidence, the bridge is UNRESOLVED regardless of how plausible the path sounds.

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
                                             INFERRED /
                                             RECONCILIATION REQUIRED)
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
                                             UNTRAVERSED /
                                             UNRESOLVED)
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
                                             DECISION + UNCERTAINTY
```

---

## Multidimensional Decision Output

Do **not** collapse the pipeline result into a single compressed label such as "MODERATE patentability." "Moderate obviousness risk" ≠ "moderate patentability" — they are not inverses. **The native output is the per-gate result table** (v1.5):

| Gate | Result |
|---|---|
| Utility | Strong / Moderate / Weak |
| Novelty / anticipation | Strongly supported / Supported / Not established |
| Causal distinction from closest prior art | Strong / Moderate / Weak (with C0–C4 / D0–D4 per reference) |
| Obviousness risk | Limited / Moderate / High — plus **UNRESOLVED** when motivation, expectation-of-success, or the causal bridge cannot be evidenced |
| Causal Bridge Test status | TRAVERSED / UNTRAVERSED / UNRESOLVED |
| Unexpected-result evidence | Present / Absent / Not observed |
| Historical disclosure coverage | Complete / Incomplete / Not evaluated |
| Commercial adoption evidence | Present / Not observed / Confirmed absent |
| Market sizing | Sufficient / Insufficient / Not evaluated |

**v1.5 rule:** there is **no "Overall patentability" row in the default output.** The per-gate table above is the only conclusion the pipeline produces. An executive score ("Indeterminate-to-[level]") may be derived **only if the user explicitly requests an executive summary score**; when derived it must be labeled as a derived executive summary (not a pipeline output), produced by the report compiler using "Indeterminate-to-[level]" as the derivation rule, and always accompanied by the full per-gate table. Never let an unresolved gate read as a resolved one.
