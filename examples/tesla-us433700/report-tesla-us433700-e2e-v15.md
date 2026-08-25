# Invention Evaluation Report — End-to-End Run (v1.5)

## Tesla US Patent 433,700 — Alternating-Current Electro-Magnetic Motor

**Report type:** Full 9-stage pipeline execution, live searches
**Framework version:** Invention Evaluation Framework **v1.5**
**Report date:** August 14, 2026
**Report file:** `report-tesla-us433700-e2e-v15.md` (v1.5 validation run; supersedes the v1.4 run `report-tesla-us433700-e2e-v14.md` in construct coverage — Causal Bridge Test, mechanism/design-choice distance, Negative Evidence Coverage Rule, Motivation Object, per-gate-only conclusion)

> **NOT LEGAL ADVICE.** This report provides a preliminary patentability assessment based on abstract-level and partial claim review. It is **NOT** a substitute for a formal patentability opinion from qualified patent counsel. It does **NOT** constitute a freedom-to-operate (FTO) opinion.

---

## Table of Contents

1. Executive Summary
2. Technology Analysis
3. Patent Landscape Analysis
4. IP / Novelty Analysis
5. Literature Search
6. Market Opportunity Analysis (1890 Historical Context)
7. Potential Partners
8. Insufficient Evidence / Not Evaluated
9. Decision Matrix Output
10. Appendices

---

## 1. Executive Summary

### 1.1 The Invention

US 433,700, granted to Nikola Tesla on August 5, 1890 (filed March 26, 1890, Serial No. 345,388; assigned to the Tesla Electric Company), claims an alternating-current motor with **two energizing-circuits** in which **interposed magnetic shields or screens** are placed between the coils and cores of one circuit **to retard the magnetization of those cores**. The shields — annealed insulated iron wire wound at right angles to the coil convolutions, forming closed magnetic circuits — delay the magnetization of the shielded core until the magnetizing current reaches a strength sufficient to saturate the shield. The result is an artificial phase difference between the two field-magnet sets from a **single alternating-current source**, producing a rotating field without a second generator.

### 1.2 Key Findings — Per-Gate Table (native output, v1.5)

| Gate | Result |
|---|---|
| **Anticipation** | NOT ANTICIPATED — no single prior-art reference discloses all claim limitations. US424,036 (granted 1890-03-25) discloses limitation (e) "retarding magnetization" directly; the interposed shield element (d) remains undisclosed in all identified prior art. |
| **Obviousness risk** | MODERATE, **UNRESOLVED** — the phase-difference problem was solved by Tesla's own US416,195 (self-induction) and the magnetic-lag concept was disclosed by US424,036 (pole geometry). The delta is the interposed shield element; motivation is PARTIALLY GROUNDED (analogous only), and the specific application is NOT OBSERVED in the accessible pre-filing record. |
| **Causal Bridge Test status** | **UNRESOLVED** — the required_change (implement known magnetic lag via a separate interposed saturable shield in a two-circuit motor) is a D3 cross-domain/application leap with no direct pre-filing teaching; neither TRAVERSED nor UNTRAVERSED is evidenced. |
| **Causal distinction from closest prior art** | Moderate-to-strong — C2/D3 vs US424,036 (same principle, different intervention point; cross-domain application of a known element); C3/D3 vs US416,195 (different physical principle; cross-domain leap). |
| **Unexpected result** | NOT IDENTIFIED — no performance comparison data exists. |
| **Commercial adoption** | NOT OBSERVED — no evidence any manufacturer adopted the shield approach; coverage LOW, insufficient to establish confirmed absence. |

**No overall patentability score is produced in this report** — the per-gate table above is the pipeline's native output (v1.5 rule). An executive score ("Indeterminate-to-moderate") may be derived on explicit request; see §9.3.

### 1.3 What Changed vs. the v1.4 Run

The v1.4 run added live verification of **seven** references and identified **two prior-art gaps** in the earlier report: **US424,036** (Tesla's magnetic-lag motor, granted 1890-03-25 — one day before US433,700 was filed) which discloses limitation (e) directly, and **US433,702** (saturable magnetic shield in a transformer, filed the same day as US433,700) which is the sibling of the motor shield, explicitly matched by Tesla's May 16, 1888 AIEE paper.

The v1.5 run **keeps those findings unchanged** (they are evidence-verified) and adds the v1.5 constructs:
1. **Mechanism distance (C0–C4)** and **design-choice distance (D0–D4)** reported per reference pathway, never combined: `C2/D3` vs US424,036; `C3/D3` vs US416,195.
2. **Causal Bridge Test** as the centerpiece of the obviousness analysis (§4.6) — states exactly what must be invented between the prior art and the claim.
3. **Negative Evidence Coverage Rule** — every NOT OBSERVED / NOT IDENTIFIED finding carries a coverage object (§8, Appendix D).
4. **First-class Motivation Object** — categorized source lists with deterministic status (PARTIALLY GROUNDED here), replacing the v1.4 inline INFERRED flag.
5. **Knowledge decomposition** — known component ≠ known function ≠ known combination ≠ known application, evidence-stated.
6. **Per-gate-only conclusion** — the "Overall patentability" row is removed (§9.2); an executive score exists only on request (§9.3).

### 1.4 Recommended Next Action

If this were a live commercial evaluation (the patent is long expired), the next step would be a targeted search of 1888–1890 issues of *The Electrician*, *Electrical World*, and *American Electrician* for any disclosure of saturation-shield phase control, plus any Tesla laboratory notes or correspondence from early 1890 documenting the shield experiments. This would upgrade the coverage of the two NOT OBSERVED findings (§8) and potentially resolve the bridge_status from UNRESOLVED.

---

## 2. Technology Analysis

### 2.1 Plain-Language Description

An AC motor whose field has two sets of coils fed from **one** alternating-current source through two branched circuits. Around the coils of one set, Tesla wraps a **magnetic shield** — layers of annealed, insulated iron wire wound at right angles to the coil convolutions, forming a closed magnetic circuit around the coil. While the current is weak, the shield absorbs the magnetic flux and protects the core from magnetization. When the current rises past a threshold, the shield **saturates** and the core magnetizes. Because the shielded core's magnetization lags the unshielded core's, the two field sets produce their maximum pull at different times — an artificial phase difference — so the field's poles appear to rotate, dragging the armature around. A variant (Fig. 2) connects the shield in series with the other circuit's coils, so the shield both retards the shielded core and accelerates the other, doubling the phase effect.

### 2.2 Feature–Benefit Map

| Feature | Benefit |
|---|---|
| Two energizing-circuits from a single AC source | No second generator or phase-splitting machinery needed |
| Interposed magnetic shield (insulated iron wire) | Retards magnetization of one core set, creating phase difference |
| Shield saturates at a predetermined current strength | Phase delay is tunable by shield thickness and material |
| Shield wound at right angles to coil convolutions | Minimizes induced currents in the shield itself |
| Shield forms a closed magnetic circuit around the coil | Concentrates the shielding effect |
| Fig. 2 variant: shield in series with the other circuit | Dual action — retards one circuit, accelerates the other |

### 2.3 Innovation Assessment

The claimed mechanism is a **material-level phase-control device**: the causal intervention point is the magnetic saturation of an interposed shield, not the electrical circuit. The specification states the shield acts in two ways — retarding the current and retarding the magnetization — which is relevant to the mechanism-distance analysis in §4.7.

### 2.4 Unexpected-Result Gate

**NOT IDENTIFIED** — no quantitative performance data (efficiency, torque, speed) comparing the shield approach against the self-induction approach (US416,195) or the magnetic-lag approach (US424,036) was found in any accessible source. Absence of a demonstrated unexpected result weakens the inventive-step argument.

### 2.5 Regulatory Burden (1890 Context)

None beyond patent grant. No safety or standards regime applied to electric motors in 1890.

### 2.6 Development Stage

| Dimension | Assessment | Evidence State | Coverage |
|---|---|---|---|
| Patent disclosure | Complete (4 claims, full spec) | CONFIRMED PRESENT | — |
| Prototype evidence | No evidence a prototype was built and tested | NOT OBSERVED | scope: Tesla prototype/test records; temporal: pre-grant; sources: patent spec, biographical record, web literature; depth: partial; completeness: LOW; limitations: laboratory notebooks not accessible |
| Production evidence | No evidence of production | NOT OBSERVED | scope: production/marketing records; temporal: 1890–1907; sources: historical company records, literature; depth: partial; completeness: LOW; limitations: no Westinghouse production records reviewed |
| Commercial adoption | No evidence any manufacturer adopted the shield approach | NOT OBSERVED | scope: commercial adoption of US433,700 shield mechanism; temporal: 1890–1907; sources: patent records, historical company records, technical literature; depth: partial; completeness: LOW; limitations: no comprehensive Westinghouse production records reviewed |

### 2.7 IPC/CPC Classification Seed

- **H02K 17/16** (asynchronous induction motors, cage rotors) — Google Patents classification for US433,700
- **H02K 17/00** (asynchronous induction motors) — family-consistent
- Related: **H01F 38/08** (high-leakage transformers — the US433,702 sibling), **H02K 23/04** (permanent-magnet-excited commutator motors — Google's modernized classification for US433,703/US424,036)

### 2.8 What Is Still Not Understood

- Whether the shield approach was more efficient, cheaper, or simpler than self-induction in practice.
- Whether the shield introduced losses (hysteresis, eddy currents in the iron wire) that offset the phase-control benefit.
- Why the approach was not adopted commercially if viable.

---

## 3. Patent Landscape Analysis

### 3.1 Search Strategy

Direct fetches of the full patent family and citation chains on Google Patents (August 14, 2026), plus web searches for the non-patent record. See Appendix E for the full query log.

### 3.2 Field Volume & Trend

The relevant field — AC motors with artificial phase difference from a single source — was dominated by Tesla's own filings between 1887 and 1890. The landscape is a **design-space exploration event by a single inventor**, not a crowded competitive field.

### 3.3 Geographic Distribution

All identified references are US patents. No international family exists for US433,700 (Country Status: US only).

### 3.4 Top Assignees & Concentration

| Assignee | Patents in scope |
|---|---|
| Nikola Tesla (individual / Tesla Electric Company) | US381,968; US382,279; US416,195; US424,036; US433,700; US433,701; US433,702; US433,703 |
| Others | None identified in the phase-control design space pre-1890 |

**Negative finding coverage:** "no other assignees identified in the phase-control design space pre-1890" — coverage: scope = assignees of AC-motor phase-control patents pre-1890; sources = Google Patents family/citation chains (single source); completeness = MEDIUM; limitations = Espacenet/Derwent/PatBase not searched.

### 3.5 CPC/IPC Subclass Concentration

H02K 17 (asynchronous motors) for the motor patents; H01F 38 (transformers) for the transformer sibling. Google's modernized classifications also assign H02P 21 (vector control) to US382,279 and H02K 23 (commutator motors) to US424,036/US433,703 — modern retro-classifications, not 1890-era classes.

### 3.6 Key Patent Profiles

| Patent | Title | Filed | Granted | Role |
|---|---|---|---|---|
| US381,968 | Electro-Magnetic Motor | 1887-10-12 | 1888-05-01 | Foundational polyphase motor (progressive pole shifting) |
| US382,279 | Electro-Magnetic Motor | 1887-11-30 | 1888-05-01 | Induction motor (rotation from reaction of induced currents) |
| US416,195 | Electro-Magnetic Motor | 1889-05-20 | 1889-12-03 | Phase difference via different self-induction + supplemental poles |
| US424,036 | Electro-Magnetic Motor | 1889-05-20 | 1890-03-25 | **Magnetic-lag motor** — poles of unequal susceptibility; retarded magnetization |
| US433,700 | Electro-Magnetic Motor | 1890-03-26 | 1890-08-05 | **Target** — interposed magnetic shield for retarding magnetization |
| US433,701 | Electro-Magnetic Motor | 1890-03-26 | 1890-08-05 | Sibling — closed magnetic iron shunts/bridges |
| US433,702 | Electrical Transformer Or Induction Device | 1890-03-26 | 1890-08-05 | Sibling — saturable magnetic shield in a transformer |
| US433,703 | Electro-Magnetic Motor | 1890-04-04 | 1890-08-05 | Sibling — core sections self-shielded from magnetization by iron layers |

**Notable pattern:** Tesla filed motor applications in **same-day pairs** — US416,195 and US424,036 both on May 20, 1889 (serials 311,419 and 311,416); US433,700, US433,701, and US433,702 all on March 26, 1890. This is direct evidence of systematic design-space exploration (§4.11).

### 3.7 Citation Signal

| Patent | Forward citations | Note |
|---|---|---|
| US381,968 | 70+ | Foundational; heavily cited |
| US382,279 | 21–28 | Includes US381,970, US401,520, US405,858, US459,772, DE975,622C, US2004/0036377A1, US2006/0045755A1 (Dell), and many Edelson/Borealis filings |
| US416,195 | 3 | US269,7809A, US269,7810A (Hutchins 1954), US2006/0045755A1 |
| US424,036 | 2 | US2006/0045755A1, US2010/0050117A1 |
| US433,700 | 1 | US2006/0045755A1 (Dell, 2006) |
| US433,702 | 11–15 | Westinghouse US2,519,224A (1950), Hutchins US2,779,907A (1957), etc. |
| US433,703 | 1 | US2006/0045755A1 |

**Forward-citation counts are a neutral historical technology-development signal, not a patentability signal.** Low counts do not establish non-obviousness (the technology may have been obvious, inferior, expensive, superseded, or commercially irrelevant). At most, low counts show later technological lineage did not strongly converge on this mechanism. Notably, the transformer sibling US433,702 drew far more later citations (11–15) than the motor patent (1) — the shield concept found its durable home in transformers, not motors.

### 3.8 Landscape Interpretation

The landscape is a single-inventor design-space exploration. US433,700 sits at the **material-dynamics corner** of Tesla's phase-control exploration, alongside the transformer shield (US433,702) and the core-geometry lag motor (US433,703). The low forward-citation count for the motor shield, contrasted with the transformer shield's citations, suggests the motor application was a technical dead end while the transformer application persisted.

---

## 4. IP / Novelty Analysis

> **NOT LEGAL ADVICE.** Preliminary patentability assessment based on abstract-level and partial claim review. **NOT** an FTO opinion.

### 4.1 Claim Construction

US433,700 contains 4 independent claims. The analysis uses **Claim 1** as the primary evaluation claim.

**Claim 1 (primary):**
> *"In an alternating-current motor having two energizing-circuits, the combination, with the magnetic cores and coils of one of the circuits, of interposed magnetic shields or screens for retarding the magnetization of said cores, as set forth."*

**Limitations:**
- (a) AC motor
- (b) Two energizing-circuits
- (c) Magnetic cores and coils of one circuit
- (d) Interposed magnetic shields/screens
- (e) For retarding magnetization of said cores

**Claim 2:** Adds — shields wound at right angles to coil convolutions
**Claim 3:** Adds — shields forming closed magnetic circuits around coils, interposed between coils and cores
**Claim 4:** Adds — insulated iron-wire shields connected in series with the other energizing-circuit's coils

### 4.2 Search Taxonomy & Queries

- Core terms: AC motor, two energizing circuits, phase difference, magnetic shield/screen, retardation, saturation
- Broader: rotating magnetic field, polyphase, induction motor, magnetic lag
- Narrower: interposed shield, iron-wire shield, closed magnetic circuit, shield in series
- Cross-referenced against H02K 17, H01F 38, H02P 21

### 4.3 Triage Results

| Reference | Date | Inventor | Relevance | Structural Relationship |
|---|---|---|---|---|
| US381,968 | 1888-05-01 | Tesla | Potentially blocking | E3 — same functional objective |
| US382,279 | 1888-05-01 | Tesla | Highly relevant | E3 — same functional objective |
| US416,195 | 1889-12-03 | Tesla | Potentially blocking | E4 — same causal architecture |
| **US424,036** | **1890-03-25** | **Tesla** | **Potentially blocking** | **E4 — same causal architecture (magnetic lag)** |
| US433,702 | 1890-08-05 | Tesla | Sibling (not prior art — same-day filing) | E4 — same mechanism, different device |
| US433,703 | 1890-08-05 | Tesla | Sibling (not prior art — filed after) | E3 — same objective, related mechanism |
| US433,701 | 1890-08-05 | Tesla | Sibling (not prior art — same-day filing) | E3 — same objective |

### 4.4 Claim-Element Mapping — US433,700 Claim 1

#### US424,036 (Tesla, 1890-03-25) — magnetic-lag motor

> Claim 1: *"In an alternating-current motor, the combination, with the armature and field-cores, of stationary energizing-coils enveloping the said cores and adapted to produce polarities or poles in both, the field-cores extending out from the coils and constructed so as to exhibit the magnetic effect imparted to them after the fall or cessation of current impulse producing such effect, as set forth."*

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "alternating-current motor" — explicit |
| (b) Two energizing-circuits | ❌ No | Single energizing coil: "both the armature and field receive their magnetism from a single energizing-coil or a plurality of coils acting as one" |
| (c) Magnetic cores and coils | ✅ Yes | Field-cores C C', energizing-coils F F — explicitly described |
| (d) Interposed magnetic shields | ❌ No | Lag achieved by pole geometry/mass/composition ("poles of unequal length, mass, or composition"), not an interposed shield element |
| (e) Retarding magnetization | ✅ Yes | "field-cores... constructed so as to exhibit the magnetic effect imparted to them after the fall or cessation of current impulse" — direct disclosure of retarded/lagging magnetization |

**Verdict:** Does NOT anticipate. Missing limitations (b) and (d).
**Structural relationship:** E4 — same causal architecture (magnetic lag), different implementation (pole properties vs. interposed shield).
**Mechanism / design-choice distance:** **C2 / D3** — same underlying physical principle (magnetic lag via saturation dynamics) applied at a different intervention point (pole-piece design → separate interposed shield element); the move from "lag built into pole geometry" to "lag produced by a separate interposed element" is a cross-domain/application leap (D3) — recognizing a known element (magnetic shield) can perform a different function (phase control), with no direct teaching of that move.

#### US416,195 (Tesla, 1889-12-03) — self-induction phase difference

> Claim 1: *"In an alternating-current motor, the combination, with an armature wound with closed coils, of a field having two or more energizing-circuits of different self-induction, whereby the currents in said circuits differ in phase, and supplemental poles situated between the primary poles and wound with coils included in derived circuits..."*

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "alternating-current motor" — explicit |
| (b) Two energizing-circuits | ✅ Yes | "two or more energizing-circuits of different self-induction" |
| (c) Magnetic cores and coils | ✅ Yes | Field-magnet with poles B B, C C, coils D, E |
| (d) Interposed magnetic shields | ❌ No | Different self-induction in circuits; supplemental poles are additional pole pieces, not shields |
| (e) Retarding magnetization | ❌ No | Phase difference from circuit-level self-induction, not from retarding core magnetization |

**Verdict:** Does NOT anticipate. Missing limitations (d) and (e).
**Structural relationship:** E4 — same causal architecture (artificial phase difference from single source), different mechanism.
**Mechanism / design-choice distance:** **C3 / D3** — different physical mechanism (circuit-level self-induction vs. material-level saturation delay) producing substantially the same effect (artificial phase difference); transferring the known "phase difference from a single source" objective onto a material-level shield element is a cross-domain/application leap (D3).

#### US381,968 (Tesla, 1888-05-01) — polyphase motor

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "alternating-current generator... progressive shifting of the poles of the motor" |
| (b) Two energizing-circuits | ✅ Yes | "separate or independent circuits on the armature or field-magnet" |
| (c) Magnetic cores and coils | ✅ Yes | Coils on ring R, armature with coils |
| (d) Interposed magnetic shields | ❌ No | No shield or screen element |
| (e) Retarding magnetization | ❌ No | Phase difference from generator, not from retarding magnetization |

**Verdict:** Does NOT anticipate. Missing (d) and (e).

#### US382,279 (Tesla, 1888-05-01) — induction motor

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "electro-magnetic motor" with "alternating currents" |
| (b) Two energizing-circuits | ✅ Yes | "independent coils" on field-magnets |
| (c) Magnetic cores and coils | ✅ Yes | Annular core A, four coils C C C C, armature disk D with coils E E |
| (d) Interposed magnetic shields | ❌ No | No shield or screen element |
| (e) Retarding magnetization | ❌ No | Rotation from reaction of induced currents, not retarded magnetization |

**Verdict:** Does NOT anticipate. Missing (d) and (e). Note: Claim 1 of US382,279 explicitly disclaims the general principle of induced currents in closed conductors, claiming only its application to this motor.

### 4.5 Anticipation Gate Result

**ALL flagged references:** Missing at least limitations (d) and (e) — with the important refinement that US424,036 now discloses (e). The only limitation missing from **every** reference is **(d) the interposed magnetic shield/screen element**.

**Gate result:** NOT ANTICIPATED by any single reference. Move to obviousness analysis.

### 4.6 Obviousness Analysis — Causal Bridge Test + Evidence Object

#### 4.6.1 Causal Bridge Test (primary pathway: closest reference US424,036)

```yaml
causal_bridge_test:
  prior_state:
    known_objective: CONFIRMED PRESENT — artificial phase difference from a single AC
                     source (US416,195; US381,968)
    known_components: CONFIRMED PRESENT — two-circuit AC motor architecture (US416,195);
                     magnetic lag via pole geometry (US424,036)
    known_principles: CONFIRMED PRESENT — magnetic saturation of iron (general
                     electromagnetic knowledge); magnetic lag (US424,036)
    knowledge_decomposition:
      component_known: CONFIRMED PRESENT — two-circuit AC motor (US416,195, US381,968);
                       magnetic shield element as phase-control device — NOT OBSERVED
      principle_known: CONFIRMED PRESENT — magnetic saturation; magnetic lag (US424,036)
      function_known:  CONFIRMED PRESENT — phase difference from single source (US416,195);
                       retarded magnetization (US424,036)
      combination_known: NOT OBSERVED — two-circuit motor + lag-via-interposed-shield
                       combination not found in accessible pre-filing record
      application_known: NOT OBSERVED — interposed saturation shield for phase control in
                       a motor not found in accessible pre-filing record
      motivation_to_combine: PARTIALLY GROUNDED (analogous evidence only)
  claimed_state:
    claimed_configuration: two energizing-circuits; interposed saturable shield between
                           coils and cores of one circuit
    claimed_effect: retarded magnetization of shielded cores -> artificial phase
                    difference -> rotating field from a single source
  bridge:
    required_change:
      - recognize that the known magnetic-lag principle (US424,036: built into pole
        geometry) can be produced by a separate interposed element
      - select a saturable magnetic shield (annealed insulated iron wire) as that element
      - interpose it between coils and cores of one circuit in a two-circuit motor
        (US416,195 architecture)
      - size/tune the shield (thickness, saturation point, winding orientation) for the
        desired phase delay
  bridge_evidence:
    direct_pre_filing: false
    analogous_pre_filing: true   # US424,036 (magnetic lag); US416,195 (phase difference)
    inventor_self_art: true      # US424,036, US416,195, US381,968, US382,279 — all Tesla's own
    general_science: true        # magnetic saturation of iron (background principle)
    post_filing: excluded        # US433,702 (shield in transformer), US433,703 — same-day /
                                 # post-filing; never count as pre-filing bridge evidence
  motivation:                    # ← first-class Motivation Object (see 4.6.3)
  expectation_of_success:
    technical: medium            # shield must be tuned; saturation delay adds hysteresis/
                                 # eddy losses; risk of interfering with the rotating field
  unexpected_result:
    identified: false
    detail: no quantitative performance comparison located
  bridge_status: UNRESOLVED
```

**Bridge interpretation:** The required_change is a **D3 cross-domain/application leap** — taking the known magnetic-lag principle and the known shield element and applying them as a phase-control mechanism in a two-circuit motor, with no direct pre-filing teaching of that specific move. Direct pre-filing bridge evidence is absent; analogous evidence (US424,036 lag, US416,195 phase difference) exists but does not teach the shield application. Because the application is NOT OBSERVED in the accessible record, bridge_status is **UNRESOLVED** — not TRAVERSED, not UNTRAVERSED.

#### 4.6.2 Obviousness Evidence Object (audit trail for the bridge test)

```yaml
obviousness_case:
  closest_reference:
    patent_or_publication: US424,036 (Tesla, 1890-03-25) — magnetic-lag motor
    relevance: E4 — same causal architecture (magnetic lag / retarded magnetization)
    mechanism_distance: C2 — same physical principle (magnetic lag), applied at a different
                        intervention point (pole-piece geometry/mass/composition vs. an
                        interposed shield element between coil and core)
    design_choice_distance: D3 — cross-domain/application leap: recognizing a known
                        element (magnetic shield) can perform a different function
                        (phase control); no direct teaching of that move
  secondary_reference:
    patent_or_publication: US416,195 (Tesla, 1889-12-03) — self-induction phase difference
    relevance: E4 — same causal architecture (artificial phase difference from single source)
    mechanism_distance: C3 — different physical principle (circuit-level self-induction vs.
                        material-level saturation delay) producing the same effect
    design_choice_distance: D3 — cross-domain/application leap (circuit domain -> material
                        domain); no direct teaching
  knowledge_decomposition:        # ← references the bridge test's prior_state (4.6.1)
    component_known: CONFIRMED PRESENT (two-circuit motor: US416,195; US381,968)
    principle_known: CONFIRMED PRESENT (magnetic saturation; magnetic lag: US424,036)
    function_known: CONFIRMED PRESENT (phase difference: US416,195; retarded magnetization: US424,036)
    combination_known: NOT OBSERVED (coverage below)
    application_known: NOT OBSERVED (coverage below)
    motivation_to_combine: PARTIALLY GROUNDED
  coverage:
    scope: interposed magnetic shield/screen as a phase-delay element in AC motors
    temporal_scope: pre-1890-03-26 (filing date)
    source_domains: [US patent full text (Google Patents), web literature, contemporary
                    technical literature (partial)]
    search_depth: full for patent records; partial for non-patent literature
    completeness: MEDIUM
    limitations: [1888-1890 electrical engineering journal full text not accessible;
                  Espacenet/Derwent/PatBase not searched]
  distinguishing_limitations:
    - limitation: (b) Two energizing-circuits
      disclosed_in_closest: no (US424,036 uses a single energizing coil)
      delta: US433,700 combines two energizing circuits with the lag concept; US416,195
             provides the two-circuit architecture
    - limitation: (d) Interposed magnetic shields/screens
      disclosed_in_closest: no
      delta: US424,036 retards magnetization via pole geometry/mass/composition;
             US433,700 interposes a separate saturable shield element between coil and core
  motivation:                    # ← first-class Motivation Object (4.6.3)
  proposed_modification_paths:
    - type: combination
      description: Combine the two-circuit AC motor of US416,195 (or US381,968) with the
                   magnetic-lag concept of US424,036, implementing the lag via an interposed
                   saturable shield rather than pole geometry
      prior_art_basis: US416,195 (two circuits, phase difference) + US424,036 (magnetic lag)
      motivation_delta: none — this path is the shared motivation analysis applied
      reasonable_expectation_of_success: medium
      compatibility_constraints: Shield must be sized to saturate at the right point in the
                   AC cycle; thickness must be tuned; shield adds material and manufacturing
                   complexity; saturation delay introduces hysteresis/eddy-current losses
                   not present in the circuit-level approach
  mechanism_displacement:
    prior_art_control_domain: magnetic_material (pole-piece geometry/mass/composition — US424,036)
                              and electrical_circuit (self-induction — US416,195)
    claimed_control_domain: magnetic_material (interposed saturable shield element)
    displacement: medium (vs. US424,036 — same principle, intervention point moves from
                  pole-piece design to a separate interposed element) / high (vs. US416,195 —
                  intervention point moves from circuit to material)
    rationale: The causal intervention point moves within the material domain (pole design
               -> separate shield element) relative to US424,036, and across domains
               (circuit -> material) relative to US416,195. Medium-to-high displacement is
               a non-obviousness argument.
  technical_effect:
    effect: Creates artificial phase difference between two field-magnet sets from a single
            AC source, enabling a rotating field without independent generators
    evidence: CONFIRMED PRESENT (mechanism described in the specification; patent granted)
              — but no quantitative performance data (NOT IDENTIFIED)
  unexpected_result: unknown — no evidence of unexpected performance advantage identified
  evidence_for_obviousness:
    - source: US424,036 (Tesla, 1890-03-25)
      supports: Discloses retarded/lagging magnetization (limitation e) directly — the
                concept of using magnetic lag for motor rotation was Tesla's own, published
                before US433,700 was filed
    - source: US416,195 (Tesla, 1889-12-03)
      supports: Establishes that artificial phase difference from a single source was a
                known goal with a working solution; the problem was already solved
    - source: US381,968 / US382,279 (Tesla, 1888)
      supports: Establish the two-circuit AC motor architecture US433,700 builds on
    - source: General electromagnetic knowledge (1885-1890)
      supports: Magnetic saturation of iron was well-known as a background principle
                (CONFIRMED PRESENT). NOTE: this establishes the principle, NOT the
                engineering application — the step from "iron saturates" to "a skilled
                engineer would choose an insulated iron-wire shield interposed between
                coil and core as a controllable phase-delay mechanism in an AC motor" is
                NOT OBSERVED in the accessible pre-filing record (knowledge
                decomposition: principle_known vs. application_known)
  evidence_against_obviousness:
    - source: US433,700 specification
      undermines: The shield operates through a physically distinct intervention point
                  (interposed saturable element) vs. US424,036's pole-piece design and
                  US416,195's circuit-level self-induction — mechanism displacement
                  supports a "different principle of operation" argument
    - source: Search results (patent + literature)
      undermines: No accessible pre-1890 source was identified describing an interposed
                  saturation shield for phase control in a motor — the specific application
                  step is NOT OBSERVED, which weakens the confidence of any obviousness finding
  neutral_signals:
    - source: Forward-citation counts (US433,700: 1; US433,702: 11-15)
      note: NOT a patentability signal. The contrast (motor shield uncited, transformer
            shield cited) is a historical technology-development signal only — it suggests
            the motor application did not persist while the transformer application did.
  unresolved_questions:
    - Was the shield approach more efficient, cheaper, or simpler than self-induction or
      pole-geometry lag in practice?
    - Did the shield introduce losses (hysteresis, eddy currents in the iron wire) that
      offset the phase-control benefit?
    - Why was this approach not adopted commercially if it was a viable alternative?
    - Is there any pre-1890 source (journal, textbook, lecture, Tesla's own notes) that
      documents saturation-shield phase delay as a design option — i.e., direct evidence
      that would upgrade the motivation from PARTIALLY GROUNDED to GROUNDED?
  evidence_state: NOT IDENTIFIED — no performance comparison data; the shield application
                  is NOT OBSERVED (coverage MEDIUM)
  final_assessment: Moderate obviousness risk, UNRESOLVED — the phase-difference problem
                  was solved by US416,195 and the magnetic-lag concept was disclosed by
                  US424,036; the delta is the interposed shield element (C2/D3 vs US424,036;
                  C3/D3 vs US416,195). The combination path is plausible with medium
                  expectation of success, but: (1) motivation is PARTIALLY GROUNDED
                  (analogous only — no direct pre-filing teaching of the shield move);
                  (2) mechanism displacement is medium-to-high, a non-obviousness argument;
                  (3) the specific application is NOT OBSERVED in the accessible pre-filing
                  record. bridge_status: UNRESOLVED. Obviousness is plausible but not
                  established.
```

#### 4.6.3 Motivation Object (first-class, v1.5)

```yaml
motivation:
  proposition: "A skilled person in early 1890 would have reason to implement magnetic
                lag via an interposed saturable shield element in a two-circuit AC motor."
  direct:
    # none — no pre-filing source teaches the interposed-shield-for-phase-delay move
  analogous:
    - source: US424,036 (Tesla, 1890-03-25)
      support: discloses magnetic lag as a motor-rotation principle (implemented via pole
               geometry) — analogous mechanism, different implementation
    - source: US416,195 (Tesla, 1889-12-03)
      support: discloses artificial phase difference from a single source (via circuit
               self-induction) — analogous objective, different mechanism
    - source: Tesla AIEE paper (1888-05-16)
      support: describes the transformer-fed two-circuit motor configuration US433,700
               implements — analogous system context
  inferred:
    - source: reasoning from general electromagnetic knowledge
      support: magnetic saturation of iron was well-known; a saturable interposed element
               is a physically plausible lag mechanism
  contradicted:
    # none identified
  status: PARTIALLY GROUNDED
```

**Derivation:** No direct evidence; ≥1 analogous (US424,036, US416,195); no unresolved contradiction → **PARTIALLY GROUNDED** per the deterministic derivation table. Note the guardrails: the three analogous sources do not accumulate into direct evidence, and the status is PARTIALLY GROUNDED, not GROUNDED. The bridge remains UNRESOLVED because the application step is NOT OBSERVED — a partially grounded motivation does not by itself traverse the bridge.

**Evidence → Inference → Conclusion firewall (finding structure):**

```yaml
finding:
  proposition: "The interposed-shield mechanism was obvious to a skilled person in 1890"

  evidence:
    - source: "US424036"
      observation: "Tesla already disclosed retarded/lagging magnetization (magnetic-lag motor), granted March 25, 1890."
    - source: "US416195"
      observation: "Tesla already used self-induction to create phase differences from a single source."
    - source: "historical electromagnetic knowledge"
      observation: "Magnetic saturation was known (background principle, CONFIRMED PRESENT)."
    - source: "search results"
      observation: "No accessible pre-1890 source was identified describing an interposed saturation shield for phase control in a motor (application step, NOT OBSERVED, coverage MEDIUM)."

  inference:
    statement: "A skilled person could potentially have implemented magnetic lag via an interposed saturable shield."
    strength: moderate

  conclusion:
    statement: "Obviousness remains plausible but is not established. Causal bridge: UNRESOLVED."
    confidence: medium
```

### 4.7 Mechanism Distance and Design-Choice Distance From Prior Art

Semantic (structural) distance, mechanism distance, and design-choice distance are **not the same thing**. US424,036 is semantically extremely close (E4 — same architecture, same objective, same physical principle) but mechanistically separated at the intervention point: lag is built into the pole pieces themselves, not produced by a separate interposed element.

| Reference | Functional similarity | Mechanism distance | Design-choice distance | Mechanism |
|---|---|---:|---:|---|
| US381,968 | High (E3) | C3 — different principle, same effect | D1/D2 — phase difference from generator is an ordinary architecture choice | Independent circuits from generator |
| US382,279 | High (E3) | C3 — different principle, same effect | D2 — non-default selection among known induction alternatives | Reaction of induced currents |
| US416,195 | Very high (E4) | C3 — different principle, same effect | D3 — circuit-level self-induction for phase delay is Tesla's own; moving to a material-level shield is an application leap | Circuit-level self-induction |
| **US424,036** | **Very high (E4)** | **C2 — same principle, different intervention point** | **D3 — recognizing a known element (shield) can perform a different function (phase control)** | **Pole geometry/mass/composition lag** |
| US433,700 (target) | — | — | — | Interposed saturable shield |
| US433,702 | Very high (E4) | C1/C2 — same principle, different device | D2 — shield-in-transformer is the same move in a directly related device | Shield in transformer |
| US433,703 | High (E3) | C2 — same principle, different intervention point | D2 — core-section self-shielding, no separate element | Core-section self-shielding |

**C and D are reported per reference pathway and never combined.** Primary pathway (closest reference): **C2/D3 vs US424,036**. Secondary pathway: **C3/D3 vs US416,195**. The D3 label is a diagnostic about the bridge, not an obviousness verdict — the motivation object (PARTIALLY GROUNDED) and the NOT OBSERVED application step determine that the bridge is UNRESOLVED.

**Interpretation:** The causal gap between US433,700 and its closest prior art runs from *pole-piece design → lag* (US424,036, C2) and *electrical inductance → phase delay* (US416,195, C3) to *interposed saturable shield → lag* (US433,700). The invention converges on the same engineering objective through a related physical principle at a **different intervention point**, and both D3 labels mark a cross-domain/application leap with no direct teaching. This gap is a genuine argument against obviousness — but it must be weighed against the fact that the problem was already solved twice over (US416,195 and US424,036), and the motivation to use a shield specifically is PARTIALLY GROUNDED (analogous only) rather than directly evidenced.

### 4.8 Per-Gate Scoring

| Axis | Score | Rationale | Evidence Status |
|---|---|---|---|
| **Utility** | **High** | Practical AC motor improvement; assigned to Tesla Electric Company; addresses real efficiency problem in single-source AC systems | CONFIRMED PRESENT (patent granted; assigned to operating company) |
| **Inventive Step** | **Moderate, unresolved** | The interposed shield is a specific, technically non-obvious solution (medium-to-high mechanism displacement; C2/C3 mechanism distance; D3 design-choice distance from closest art). However, the problem (artificial phase difference from single source) was already solved by US416,195, and the lag concept was disclosed by US424,036. The shield is an alternative means to the same end. Motivation is PARTIALLY GROUNDED (analogous only); the application is NOT OBSERVED. Bridge status UNRESOLVED. | NOT IDENTIFIED (no unexpected result data); application NOT OBSERVED (coverage MEDIUM) |
| **Novelty** | **Moderate–High** | No single prior art reference anticipates all claim limitations. The interposed shield element (limitation d) is new. However, the invention builds directly on Tesla's own 1887–1890 patent portfolio. | CONFIRMED PRESENT (no anticipating reference found) |

### 4.9 Combination-Obviousness Exposure (Derivation Risk)

**This is not "combination novelty."** A combination can be completely novel while still being obvious — novelty and obviousness are different questions. The operative question is **derivation risk**: how readily can the claimed combination be reconstructed from prior-art components, with a demonstrated motivation to combine?

| Component | Where it exists in prior art | Evidence |
|---|---|---|
| AC motor with two energizing circuits | US381,968 (1888), US416,195 (1889) | CONFIRMED PRESENT |
| Artificial phase difference from single source | US416,195 (1889) | CONFIRMED PRESENT |
| Retarded/lagging magnetization | **US424,036 (granted 1890-03-25)** | **CONFIRMED PRESENT** |
| Magnetic shielding of coils | General electromagnetic knowledge | CONFIRMED PRESENT (principle) |
| **Delta: interposed saturable shield as the lag mechanism in a two-circuit motor** | **Not identified in accessible pre-1890 record** | **NOT OBSERVED** (coverage MEDIUM) |

**Knowledge-decomposition framing (v1.5):** `component_known` (two-circuit motor), `principle_known` (saturation, magnetic lag), and `function_known` (phase difference, retarded magnetization) are all CONFIRMED PRESENT. What is NOT OBSERVED is `combination_known` and `application_known` — the specific move of using an interposed shield as the lag mechanism in a two-circuit motor. This is exactly the structural distinction the knowledge decomposition exists to enforce: known parts and known functions do not make the application known.

**Derivation assessment:** The components exist — including, newly, the lag concept itself (US424,036). The delta step is the *application* of the lag concept via an interposed shield element in a two-circuit motor. That application is NOT OBSERVED in the accessible record, and no direct source evidences a motivation to make this specific substitution (motivation PARTIALLY GROUNDED — analogous only). Derivation risk is therefore **moderate and unresolved** — the combination is not established as obvious, but the absence of a demonstrated unexpected result and the partially grounded motivation leave the inventive-step case incomplete. The unexpected-result gate returned **NOT IDENTIFIED**.

### 4.10 Self-Prior-Art Exposure

The closest references are Tesla's own earlier filings:

| Risk Type | Assessment |
|---|---|
| **Anticipation exposure** | LOW — no own prior patent discloses limitation (d) (interposed shield) |
| **Obviousness exposure** | MODERATE, UNRESOLVED — US416,195 solves the phase-difference problem and US424,036 discloses the lag concept; the shield substitution is plausible but motivation is PARTIALLY GROUNDED and the application NOT OBSERVED |
| **Double-patenting exposure** | MODERATE — US416,195, US424,036, and US433,700 all claim phase/lag-based motor operation from a single source; different mechanisms but overlapping functional results |
| **Family/priority relationship** | None — US433,700 is a separate filing (Serial No. 345,388), not a continuation or divisional of US416,195 (Serial No. 311,419) or US424,036 (Serial No. 311,416) |

### 4.11 Design-Space Position

US433,700 is best understood not as an isolated invention but as one node in a **design-space exploration event**: Tesla was implementing the same higher-level architecture — *artificial phase difference from a single AC source* — through multiple physical mechanisms in rapid succession, often filing same-day pairs.

```text
                         PHASE DIFFERENCE
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   Independent circuits   Self-induction       Magnetic lag
      US381968              US416195        US424036 (pole geometry)
          │                    │                    │
          ▼                    ▼                    ▼
    electrical source     circuit dynamics     material dynamics
                                                    │
                                                    ▼
                                          US433700 (interposed shield)
                                          US433702 (shield in transformer)
                                          US433703 (core-section self-shielding)
```

**Same-day filing pairs (design-space evidence):**
- **1889-05-20:** US416,195 (self-induction) + US424,036 (magnetic lag) — two mechanisms, one day
- **1890-03-26:** US433,700 (shield in motor) + US433,701 (iron shunts) + US433,702 (shield in transformer) — three filings, one day
- **1890-04-04:** US433,703 (core-section self-shielding) — the lag concept implemented without any separate shield element

**Interpretation:** This pattern reframes the evaluation question from "is this patent novel?" to "what region of the inventor's design space does this invention occupy?" US433,700 sits at the material-dynamics corner of Tesla's exploration of phase-control mechanisms, flanked by the transformer shield (US433,702) and the core-geometry lag motor (US433,703). This is contextual evidence about the inventor's working method — it does not by itself establish or refute patentability, but it explains why the shield patent reads as a deliberate exploration of an alternative mechanism rather than a marginal variation of US416,195 or US424,036.

---

## 5. Literature Search

### 5.1 Search Queries

- Q1: Ferraris rotating magnetic field 1885 / 1888 publication
- Q2: Tesla 1888 AIEE paper "A New System of Alternate Current Motors and Transformers"
- Q3: Magnetic saturation / shielding knowledge pre-1890
- Q4: Contemporary electrical engineering journals (1888–1890 window)

### 5.2 Findings

| Source | Date | Relevance | Key Content |
|---|---|---|---|
| **Ferraris, "Electrodynamic rotations produced by means of alternate currents"** | Published 1888-03-11 (Royal Academy of Sciences, Turin) | Background | Rotating magnetic field from two sine-wave AC currents 90° apart; phase-splitting via resistance vs. self-inductance branches. Ferraris conceived/demonstrated the principle in 1885; did not patent. |
| **Tesla, "A New System of Alternate Current Motors and Transformers"** | AIEE lecture 1888-05-16 (published in Transactions, DOI 10.1109/T-AIEE.1888.5570379) | **Highly relevant** | Describes the full polyphase system. **Explicitly describes "a motor with one of its circuits in series with a transformer and the other in the secondary of the transformer"** — the exact configuration of US433,700 Fig. 2 and US433,702 Fig. 2. Confirms the shielded transformer (US433,702) was designed to feed the shielded motor (US433,700): a matched pair. |
| **Baily (1879)** | 1879 | Background | First primitive induction motor (commutator-switched electromagnets producing rotating field). |
| **Dolivo-Dobrovolsky** | 1889 | Background | Three-phase squirrel-cage induction motor (AEG) — the design that ultimately won the induction-motor race. |
| **Contemporary journals (1888–1890)** | 1888–1890 | **Insufficient evidence** | Full-text access to *The Electrician*, *Electrical World*, *American Electrician* for this window not available; no accessible non-patent disclosure of saturation-shield phase control identified. |

### 5.3 Key Technical Context

- **Rotating magnetic field theory** (Ferraris 1885/1888; Tesla 1888): Well-established by 1890.
- **Self-induction / phase retardation**: Standard electromagnetic knowledge by 1890.
- **Magnetic saturation of iron**: Well-known phenomenon (background principle, CONFIRMED PRESENT).
- **Magnetic lag**: Disclosed by Tesla himself in US424,036 (filed 1889-05-20, granted 1890-03-25).
- **Magnetic shielding**: Known in general, but **application to AC motor phase control via an interposed saturation shield is not found in accessible pre-1890 non-patent literature**.

### 5.4 Evidence-State Assessment (with coverage objects, v1.5)

| Claim | Evidence State | Coverage |
|---|---|---|
| Non-patent literature discloses an interposed shield for phase delay before March 26, 1890 | **NOT IDENTIFIED** | scope: interposed shield/screen for phase delay in AC motors; temporal: pre-1890-03-26; source_domains: web literature, journal indexes; depth: partial; completeness: LOW (1888–1890 journal full text not accessible) |
| Rotating magnetic field concept was known before 1890 | **CONFIRMED PRESENT** | — (Ferraris 1885/1888, Tesla 1888) |
| Magnetic saturation of iron was known before 1890 | **CONFIRMED PRESENT** | — (general electromagnetic knowledge) |
| Magnetic lag for motor operation was known before 1890 | **CONFIRMED PRESENT** | — (US424,036, Tesla, granted 1890-03-25) |
| Specific interposed-shield-for-phase-delay mechanism appears in non-patent literature | **NOT IDENTIFIED** | same coverage as row 1 (completeness: LOW) |

### 5.5 Assessment

**Insufficient evidence** for a non-patent publication disclosing the specific interposed-shield-for-phase-delay mechanism before the March 26, 1890 filing date. Full-text access to 1888–1890 issues of *The Electrician*, *Electrical World*, and *American Electrician* would be needed to confirm absence of non-patent disclosure. Under the Negative Evidence Coverage Rule, these findings stay at NOT IDENTIFIED with LOW coverage — they cannot be upgraded toward CONFIRMED ABSENT without the denser record.

---

## 6. Market Opportunity Analysis (1890 Historical Context)

### 6.1 Target Market & Buyer Profile

| Segment | Buyer Profile | Size (1890 est.) | Evidence State |
|---|---|---|---|
| Industrial power transmission | Manufacturing plants, mills, factories | Rapidly growing; AC winning "War of Currents" | CONFIRMED PRESENT (historical record) |
| Electric lighting systems | Municipal utilities, building operators | Expanding; AC preferred for long-distance distribution | CONFIRMED PRESENT |
| Railway electrification (early) | Streetcar operators | Emerging; DC dominant but AC being explored | CONFIRMED PRESENT |
| Mining & heavy industry | Mine operators, ore processing | Niche but high-value; remote sites favor AC | CONFIRMED PRESENT |

### 6.2 NAICS Equivalent

No NAICS code existed in 1890. Retroactively: **335312 (Motor and Generator Manufacturing)**, **221115 (Electric Power Distribution)**.

### 6.3 Market Sizing

| Metric | Value | Source |
|---|---|---|
| Total US electrical industry revenue (1890) | **Not established** — no sufficiently reliable primary-source dataset identified to calculate a defensible figure | NOT IDENTIFIED in primary source |
| Motor segment | <5% of total; AC motors were a tiny fraction | Derived from historical electrification data (INFERRED) |
| Growth rate (AC motor adoption 1890–1900) | **Not established** — no reliable primary-source dataset identified to calculate a defensible CAGR | NOT IDENTIFIED |
| Addressable market for this invention | Subset of AC motor market where single-source phase control is needed | Derived (INFERRED) |

**Qualitative statement (defensible):** AC electrical infrastructure was undergoing rapid expansion during the period — the "War of the Currents" was being won by AC for long-distance distribution, and Westinghouse's 1893 World's Fair contract was a watershed. But no sufficiently reliable primary-source dataset was identified to calculate a defensible CAGR for AC motor adoption. **That qualitative statement is more useful than an impressive-looking number with no reconstructable basis.**

### 6.4 Competitive Landscape

| Competitor | Technology | Position | IP Posture |
|---|---|---|---|
| Edison General Electric (DC) | DC motors, direct distribution | Losing ground on long-distance; dominant in urban centers | Strong DC patent portfolio; declining relevance |
| Westinghouse Electric | AC systems (Tesla-licensed) | Gaining; 1893 World's Fair will be watershed moment | Holds Tesla's core AC patents via 1888 licensing deal |
| Thomson-Houston Electric | Arc lighting, AC dynamos | Major player; merged into GE in 1892 | Moderate patent portfolio |
| Independent AC motor inventors | Various designs (Ferraris, Bradley, Dolivo-Dobrovolsky) | Fragmented; no dominant design yet | Sparse patent coverage; Dolivo-Dobrovolsky's three-phase cage motor (1889) would become the dominant design |

### 6.5 Commercial Actionability Assessment

| Factor | Assessment | Evidence State |
|---|---|---|
| Clear buyer | ✅ Industrial operators, utilities | CONFIRMED PRESENT |
| Feasible production cost | ✅ Iron wire, copper coils — standard materials | CONFIRMED PRESENT |
| Accessible regulatory pathway | ✅ Patent granted; no additional approvals needed | CONFIRMED PRESENT |
| Viable competitive position | ⚠️ Depends on Westinghouse licensing; Tesla Electric Company was financially strained; Dolivo-Dobrovolsky's three-phase design was emerging as the industry standard | NOT IDENTIFIED — no evidence of standalone competitive viability |
| **Overall commercial actionability** | **Moderate** — technically viable, but commercial success depended on corporate licensing, not just the patent itself | — |

**Scoring:** Market size (med) × Growth (high, qualitative — directional only, no defensible CAGR) × Accessibility (med) × Competitive intensity (med) = **Moderate**, no "low" scores.

### 6.6 Technical Maturity vs. Commercial Readiness

| Dimension | Assessment | Evidence State | Coverage |
|---|---|---|---|
| Patent disclosure | CONFIRMED PRESENT | Patent granted Aug 5, 1890 | — |
| Engineering feasibility | High | Standard materials; no exotic manufacturing needed | — |
| Prototype evidence | NOT OBSERVED | No evidence found that a prototype was built and tested; coverage insufficient to establish it never was | scope: prototype/test records; completeness: LOW |
| Production evidence | NOT OBSERVED | No evidence of production; coverage insufficient to establish absence | scope: production records; completeness: LOW |
| Commercial adoption evidence | NOT OBSERVED | No evidence found that Westinghouse or any manufacturer adopted the shield approach in production motors — the historical record is not dense enough to establish confirmed absence (no bounded universe defined) | scope: commercial adoption of US433,700 shield mechanism; temporal: 1890–1907; source_domains: patent records, historical company records, technical literature; depth: partial; completeness: LOW; limitations: no comprehensive Westinghouse production records reviewed |
| **Commercial readiness** | **NOT EVALUATED** | No confirmed adoption evidence exists | — |

### 6.7 SWOT

| Strengths | Weaknesses |
|---|---|
| Eliminates need for independent generators | No standalone product value — component improvement only |
| Tunable phase delay via shield thickness | Shield adds material and manufacturing complexity |
| Uses standard materials (iron wire, copper) | No demonstrated performance advantage over self-induction (US416,195) or pole-geometry lag (US424,036) |
| Patent granted and assigned to operating company | Tesla Electric Company financially strained |
| **Opportunities** | **Threats** |
| AC motor market growing rapidly (qualitative — CAGR not defensibly quantifiable) | Self-induction approach (US416,195) and magnetic-lag approach (US424,036) are established alternatives |
| Westinghouse licensing deal could incorporate improvement | Technology substitution risk — Dolivo-Dobrovolsky's three-phase cage motor (1889) became the industry standard |
| Industrial electrification expanding | Edison's DC system still dominant in urban centers |
| Mining and remote industrial sites favor AC | No evidence of commercial adoption (NOT OBSERVED, coverage LOW) |

### 6.8 Key Market Risks

1. **Tesla Electric Company financial instability** — Tesla's own company was struggling; the patent was assigned to them but they lacked manufacturing capacity.
2. **Westinghouse licensing dependency** — Westinghouse held the broader polyphase patent portfolio (US381,968 etc.). The shield improvement was valuable primarily within the Westinghouse system.
3. **Technology substitution risk** — Self-induction (US416,195), pole-geometry lag (US424,036), and ultimately three-phase cage motors (Dolivo-Dobrovolsky) were alternative approaches; the market standardized on three-phase.
4. **No standalone product** — this was a component improvement, not a complete motor; value depended on system integration.

---

## 7. Potential Partners

### 7.1 Primary Recommendation: Westinghouse Electric (Pittsburgh)

| Field | Value |
|---|---|
| **Organization** | Westinghouse Electric & Manufacturing Company |
| **Location** | Pittsburgh, PA |
| **Business description** | AC power systems, motors, generation equipment; Tesla's primary commercial partner via 1888 licensing deal |
| **Relevance rationale** | Westinghouse already held Tesla's core polyphase patent portfolio (US381,968 etc.). The shield improvement would be valuable primarily within the Westinghouse system — it is a component, not a standalone product. Westinghouse represented the **strongest identified commercialization pathway** because of its existing Tesla licensing relationship, manufacturing capability, and AC system position. This is not an exclusivity claim: the record does not establish that no other pathway existed, only that none was identified (NOT OBSERVED). |
| **Proposed partnership model** | Licensing (fold into existing Tesla-Westinghouse patent agreement) |
| **Fit** | **High** — the strongest identified partner with the manufacturing capacity and market position to commercialize this improvement |
| **Likelihood** | Moderate — Westinghouse already had US416,195's self-induction approach and US424,036's lag approach; would need to see efficiency advantage to adopt the shield alternative |

### 7.2 Secondary Options

| Partner | Role | Fit | Likelihood | Reasoning |
|---|---|---|---|---|
| Thomson-Houston Electric (Lynn, MA) | Alternative AC system manufacturer | Medium | Moderate | Competitor to Westinghouse; could license as alternative, but lacks Tesla system integration |
| Tesla Electric Company (New York) | Already assignee; limited manufacturing capacity | Medium | Moderate | Financially strained; could sublicense but lacks production capability |
| Municipal electric utilities | Early adopters / demonstration sites | Low | Low | Early stage; limited capital; would need complete motor system, not component |
| AIEE (American Institute of Electrical Engineers) | Technical validation and publication | Low | Moderate | Tesla presented at AIEE meetings; could build technical credibility but not commercial path |

### 7.3 Partnership Risks

| Risk | Mitigation |
|---|---|
| Westinghouse already has equivalent solutions (US416,195, US424,036) | Demonstrate efficiency advantage of shield approach — **but no performance data exists** |
| Tesla Electric Company financial instability | Structure deal as patent assignment or licensing, not equity |
| No standalone product value | Bundle with full motor system design; sell as system improvement, not component |
| Shield approach never commercially adopted | NOT OBSERVED — no evidence of adoption found; historical record insufficient to establish confirmed absence (coverage LOW) |

---

## 8. Insufficient Evidence / Not Evaluated

This section surfaces all NOT IDENTIFIED and NOT OBSERVED flags from upstream skills with their **coverage objects** (v1.5 Negative Evidence Coverage Rule). These are **not buried in appendices** — they are required outputs per the framework's evidence-state discipline.

| # | Item | Evidence State | Coverage |
|---|---|---|---|
| 1 | Non-patent literature disclosing an interposed shield for phase delay before March 26, 1890 | **NOT IDENTIFIED** | scope: interposed shield/screen for phase delay in AC motors; temporal: pre-1890-03-26; source_domains: web literature, journal indexes; depth: partial; completeness: LOW; limitations: 1888–1890 journal full-text not accessible |
| 2 | Quantitative performance data (efficiency, torque, speed) for the shield design | **NOT IDENTIFIED** | scope: performance comparison shield vs. self-induction vs. pole-geometry lag; completeness: LOW; limitations: no accessible source contains performance data |
| 3 | Unexpected technical result from the combination | **NOT IDENTIFIED** | same coverage as item 2 (no comparison data) |
| 4 | Commercial adoption of the shield approach | **NOT OBSERVED** | scope: commercial adoption of US433,700 shield mechanism; temporal: 1890–1907; source_domains: patent records, historical company records, technical literature; depth: partial; completeness: LOW; limitations: no comprehensive Westinghouse production records reviewed |
| 5 | Prototype evidence | **NOT OBSERVED** | scope: prototype/test records; temporal: pre-grant; completeness: LOW |
| 6 | Production evidence | **NOT OBSERVED** | scope: production records; temporal: 1890–1907; completeness: LOW |
| 7 | Commercial readiness | **NOT EVALUATED** | — (no confirmed adoption evidence; stated as NOT EVALUATED per framework rule) |
| 8 | Market sizing (1890 electrical industry revenue, AC motor CAGR) | **NOT IDENTIFIED** | scope: primary-source revenue/CAGR datasets; completeness: LOW; limitations: no sufficiently reliable primary-source dataset identified |
| 9 | Full-text access to 1888–1890 electrical engineering journals | **NOT EVALUATED** | — (search not performed due to access limitations) |
| 10 | Motivation for substituting an interposed shield for self-induction or pole-geometry lag | **PARTIALLY GROUNDED** (analogous only) | sources: US424,036, US416,195, Tesla AIEE 1888 paper (analogous); no direct pre-filing source. Caps the bridge at UNRESOLVED |
| 11 | Whether the shield approach was ever reduced to practice by Tesla | **NOT OBSERVED** | scope: prototype/test evidence; completeness: LOW |

**Coverage note (v1.5):** none of the above findings may be upgraded toward CONFIRMED ABSENT. The adoption finding (item 4) in particular would require a bounded evidence universe (e.g., "all Westinghouse production motor models 1890–1907") with documented completeness — no such universe was available. Coverage is metadata, not evidence.

---

## 9. Decision Matrix Output

### 9.1 State Machine Path

```text
PRIOR ART REFERENCES (US381,968; US382,279; US416,195; US424,036)
                    │
                    ▼
            ┌─────────────────┐
            │ Claim mapping    │
            └────────┬────────┘
                     │
                     ▼
          ANY LIMITATION MISSING?
                     │
                    YES (all references missing (d);
                         US424,036 discloses (e))
                     │
                     ▼
          OBVIOUSNESS ANALYSIS
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
  Modify         Combine         Substitute
                                   │
                                   ▼
                        MOTIVATION OBJECT
                        (PARTIALLY GROUNDED —
                         analogous only:
                         US424,036, US416,195,
                         AIEE 1888 paper;
                         no direct pre-filing
                         teaching of the shield move)
                                   │
                                   ▼
                        EXPECTED-SUCCESS GATE
                        (medium, capped by
                         compatibility constraints)
                                   │
                                   ▼
                        CAUSAL BRIDGE TEST
                        (prior_state -> claimed_state ->
                         required_change (D3 leap) ->
                         bridge_evidence:
                         direct_pre_filing: false,
                         analogous: true,
                         post_filing: excluded)
                                   │
                                   ▼
                        BRIDGE STATUS: UNRESOLVED
                        (application NOT OBSERVED;
                         motivation not GROUNDED)
                                   │
                                   ▼
                        MECHANISM-DISTANCE +
                        DESIGN-CHOICE DISTANCE
                        (C2/D3 vs US424,036;
                         C3/D3 vs US416,195 —
                         reported per pathway,
                         never combined;
                         mechanism displacement
                         MEDIUM-to-HIGH)
                                   │
                                   ▼
                        TECHNICAL EFFECT
                        (phase difference from single source)
                                   │
                        UNEXPECTED RESULT?
                                   │
                        NOT IDENTIFIED
                                   │
                                   ▼
                        EVIDENCE FIREWALL
                        (no inference promoted to fact)
                                   │
                                   ▼
                        CONCLUSION:
                        Moderate obviousness risk, UNRESOLVED
                        (motivation PARTIALLY GROUNDED,
                         medium-to-high mechanism displacement,
                         application NOT OBSERVED,
                         bridge_status UNRESOLVED)
```

### 9.2 Conclusion — Per-Gate Table (native output, no overall row)

| Gate | Result |
|---|---|
| **Anticipation gate** | NOT ANTICIPATED — no single reference discloses all limitations; (d) interposed shield missing from all references; (e) now disclosed in US424,036 |
| **Obviousness analysis** | MODERATE RISK, **UNRESOLVED** — substitution of an interposed shield for self-induction (US416,195) or pole-geometry lag (US424,036) is a plausible modification path; motivation is PARTIALLY GROUNDED (analogous only, not direct); mechanism displacement is MEDIUM-to-HIGH; the specific application is NOT OBSERVED in the accessible pre-filing record (coverage MEDIUM) |
| **Causal Bridge Test** | **UNRESOLVED** — required_change is a D3 cross-domain/application leap; direct pre-filing bridge evidence absent; analogous evidence does not traverse the bridge; application NOT OBSERVED |
| **Causal distinction from closest prior art** | **Moderate-to-strong** — C2/D3 vs US424,036 (same principle, different intervention point; application leap); C3/D3 vs US416,195 (different physical principle; application leap) |
| **Technical effect** | CONFIRMED PRESENT — phase difference from single source is achieved |
| **Unexpected result** | NOT IDENTIFIED — no performance comparison data available (coverage LOW) |
| **Combination-obviousness exposure** | MODERATE, UNRESOLVED — components exist in prior art (including the lag concept in US424,036); knowledge decomposition: component/principle/function known, combination/application NOT OBSERVED; derivation not established |
| **Self-prior-art** | MODERATE RISK — Tesla's own US416,195 and US424,036 are the closest references; double-patenting exposure exists |
| **Historical disclosure coverage** | **Incomplete** — 1888–1890 journal full-text not accessible; application step NOT OBSERVED (coverage MEDIUM/LOW) |
| **Commercial adoption evidence** | **NOT OBSERVED** — no adoption found; coverage LOW, no bounded universe defined (cannot be CONFIRMED ABSENT) |
| **Historical market sizing** | **Insufficient** — no defensible CAGR or revenue figure reconstructable from primary sources |

**No "Overall patentability" row is produced** (v1.5 rule). "Moderate obviousness risk" ≠ "moderate patentability" — they are not inverses, and no single scalar is derived from the independent gate results by default.

### 9.3 Executive Score (derived only on request)

If an executive summary score is requested, the report compiler derives it per the framework rule: **INDETERMINATE-TO-MODERATE** — strong on utility, novelty, and causal distinction; obviousness risk moderate but unresolved (bridge_status UNRESOLVED); unexpected-result evidence absent; historical evidence coverage incomplete. **This is a derived executive summary, not a pipeline output.** It is valid only together with the full per-gate table in §9.2.

---

## 10. Appendices

### Appendix A: Original Submission Record

| Field | Value |
|---|---|
| **Invention name** | Alternating-Current Electro-Magnetic Motor |
| **Patent number** | US 433,700 |
| **Inventor** | Nikola Tesla (of New York, N.Y.) |
| **Assignee** | Tesla Electric Company |
| **Filed** | March 26, 1890 (Serial No. 345,388) |
| **Patented** | August 5, 1890 |
| **Status** | Historical term expired: August 5, 1907 (17 years from grant, subject to the historical patent regime) |
| **Classification** | H02K 17/16 (asynchronous induction motors, cage rotors) |
| **Short description** | AC motor using interposed magnetic shields to create artificial phase difference between field magnet sets from a single current source |
| **Detailed description** | Two sets of field-magnet cores, each wound with coils in separate branched circuits from a single AC source. Magnetic shield (annealed insulated iron wire) around one set of coils delays magnetization via saturation, creating phase difference. Fig. 2 variant: shield connected in series with other circuit for dual acceleration/retardation effect. |
| **Innovation claims** | 4 independent claims covering magnetic shield/screen interposed between coils and cores to retard magnetization |
| **Proof-of-concept** | Patent granted; assigned to operating company |
| **Current IP status** | Historical term expired: August 5, 1907 (17 years from grant, subject to the historical patent regime) |
| **Target markets** | Industrial power transmission, electric lighting systems, emerging AC distribution infrastructure |
| **Known competitors** | Edison General Electric (DC), Westinghouse Electric (AC), Thomson-Houston Electric |
| **Disclosure history** | No public disclosure prior to filing identified. Patent application filed March 26, 1890. **NOT OBSERVED** — no earlier talks, publications, demonstrations, sale offers, or social media posts identified in searched sources; coverage insufficient to establish confirmed absence. (Not to be conflated with "confirmed absent.") |
| **Source document** | Full patent text retrieved from Google Patents: https://patents.google.com/patent/US433700A/en |

### Appendix B: Patentability Primer

- **Anticipation:** A single prior-art reference discloses every element of a claim. None of the identified references anticipate US433,700 Claim 1 — all are missing limitation (d) (interposed shield); US424,036 additionally discloses (e) but misses (b) and (d).
- **Obviousness / Inventive Step:** Two or more references, combined, disclose every element, with a plausible reason a skilled person would combine them. Risk is moderate but unresolved — Tesla's own prior patents provide the closest combination risk. The substitution of an interposed shield for self-induction or pole-geometry lag is the primary obviousness path, but the motivation for it is PARTIALLY GROUNDED (analogous only) rather than directly evidenced, mechanism displacement is medium-to-high, and the Causal Bridge Test returns UNRESOLVED.
- **Combination-Obviousness Exposure:** Novelty argued from combining known elements rather than a new element itself — the weakest basis for an inventive-step argument absent an unexpected result. **A combination can be completely novel while still being obvious.** The operative question is derivation risk: how readily the combination can be reconstructed from prior-art components with a demonstrated motivation to combine. **This applies to US433,700.**
- **Freedom to Operate (FTO):** A search for *in-force* patents the invention might infringe. This report does **NOT** provide an FTO opinion. The patent is expired, so FTO concerns are moot for this specific invention, but this analysis should not be generalized to other inventions.

### Appendix C: Search Methodology

All searches were conducted using publicly available patent databases (Google Patents) and web search tools. Searches were performed on August 14, 2026. No proprietary patent databases (Derwent, PatBase, etc.) were used. Non-patent literature searches were conducted via web search; full-text access to 1888–1890 electrical engineering journals was not available.

**Databases searched:**
- Google Patents (full-text patent search, citation chains, similar documents)
- Web search (Ferraris, Tesla AIEE paper, induction motor history)

**Databases NOT searched (access limitations):**
- Espacenet (returned 403 error in prior runs)
- Derwent, PatBase (proprietary, not available)
- IEEE Xplore full text (abstract/index only for the 1888 paper)
- *The Electrician*, *Electrical World*, *American Electrician* (full-text not accessible for 1888–1890 window)

**Coverage note:** Per the Negative Evidence Coverage Rule, the patent-record searches (Google Patents direct fetches, full text) are completeness MEDIUM; the non-patent searches (web literature) are completeness LOW. No negative finding in this report relies on coverage above MEDIUM.

### Appendix D: Evidence Audit

| Key Claim | Evidence Status | Coverage / Source Searched |
|---|---|---|
| No single reference anticipates US433,700 Claim 1 | CONFIRMED PRESENT | Google Patents — US381,968, US382,279, US416,195, US424,036 full text reviewed |
| US424,036 discloses retarded/lagging magnetization (limitation e) | CONFIRMED PRESENT | Google Patents — US424,036 full text reviewed (granted 1890-03-25, one day before US433,700 filed) |
| US416,195 is the closest prior art for two-circuit phase difference | CONFIRMED PRESENT | Google Patents — US416,195 full text reviewed |
| The interposed shield element is not found in pre-1890 prior art | NOT OBSERVED | coverage: scope = interposed saturable shield for motor phase control; temporal = pre-1890-03-26; sources = Google Patents + web; completeness = MEDIUM |
| The shield mechanism is not found in pre-1890 non-patent literature | NOT IDENTIFIED | coverage: sources = web search (Ferraris, Tesla AIEE, journal history); completeness = LOW (journal full text not accessible) |
| The shield approach was not commercially adopted | NOT OBSERVED | coverage: temporal = 1890–1907; sources = historical record; completeness = LOW; no bounded universe defined — cannot be CONFIRMED ABSENT |
| No unexpected result data exists | NOT IDENTIFIED | coverage: scope = performance comparison data; completeness = LOW |
| US433,700 has 1 forward citation | CONFIRMED PRESENT | Google Patents — Cited By section: US2006/0045755A1 (Dell, 2006) |
| US381,968 has 70+ forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US416,195 has 3 forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US382,279 has 21+ forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US424,036 has 2 forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US433,702 has 11–15 forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US433,703 has 1 forward citation | CONFIRMED PRESENT | Google Patents — Cited By section |
| US433,700 and US433,702 filed the same day (1890-03-26) | CONFIRMED PRESENT | Google Patents — both specifications: "Application filed March 26, 1890" |
| US416,195 and US424,036 filed the same day (1889-05-20) | CONFIRMED PRESENT | Google Patents — both specifications: "Application filed May 20, 1889" |
| No international patent family for US433,700 | CONFIRMED PRESENT | Google Patents — Country Status: US (1) only |
| Tesla assigned patent to Tesla Electric Company | CONFIRMED PRESENT | Patent specification header: "ASSIGNOR TO THE TESLA ELECTRIC COMPANY" |
| Filing date March 26, 1890 | CONFIRMED PRESENT | Patent specification: "Application filed March 26, 1890. Serial No. 345,388" |
| Tesla's 1888 AIEE paper describes transformer-fed two-circuit motor | CONFIRMED PRESENT | AIEE lecture text (May 16, 1888) — "a motor with one of its circuits in series with a transformer and the other in the secondary of the transformer" |

### Appendix E: Full Query Log

| # | Query String | Database | Date | Results Used |
|---|---|---|---|---|
| 1 | `US433700A` direct fetch | Google Patents | 2026-08-14 | Full patent text, claims, classification, citations, similar documents |
| 2 | `US381968A` direct fetch | Google Patents | 2026-08-14 | Full patent text, claims, 70+ citations |
| 3 | `US382279A` direct fetch | Google Patents | 2026-08-14 | Full patent text, claims, 21+ citations |
| 4 | `US416195A` direct fetch | Google Patents | 2026-08-14 | Full patent text, claims, 3 citations |
| 5 | `US424036A` direct fetch | Google Patents | 2026-08-14 | **NEW** — magnetic-lag motor, full text, claims, 2 citations |
| 6 | `US433701A` direct fetch | Google Patents | 2026-08-14 | Sibling — iron shunts/bridges |
| 7 | `US433702A` direct fetch | Google Patents | 2026-08-14 | Sibling — shield in transformer, full text, claims, 11–15 citations |
| 8 | `US433703A` direct fetch | Google Patents | 2026-08-14 | Sibling — core-section self-shielding, full text, claims |
| 9 | `Ferraris 1885 rotating magnetic field experiment electromagnetic motor history` | Web search | 2026-08-14 | Ferraris 1885/1888 timeline, Baily 1879, Dolivo-Dobrovolsky 1889 |
| 10 | `Tesla 1888 AIEE paper "A New System of Alternating Current Motors and Transformers" magnetic lag shield` | Web search | 2026-08-14 | AIEE lecture text (May 16, 1888), DOI 10.1109/T-AIEE.1888.5570379, transformer-fed motor configuration |

### Appendix F: Quality Checklist (v1.5)

- [x] Every quantitative claim is sourced (or omitted / marked INFERRED with derivation — unsourced revenue and CAGR figures removed)
- [x] Chronology validator passed: all dates consistent; US424,036 granted 1890-03-25 (one day before US433,700 filed 1890-03-26) — correctly treated as prior art; US433,702 same-day filing and US433,703 post-filing correctly excluded as prior art
- [x] Every legal-adjacent statement (patentability, FTO-adjacent, regulatory) carries a "not legal advice" disclaimer
- [x] The novelty section explicitly states it is not an FTO opinion
- [x] The query log is complete enough that a reviewer could re-run any search and reproduce the result set
- [x] Any "NOT IDENTIFIED", "NOT OBSERVED", or "NOT EVALUATED" flags from upstream skills are carried into the report (Section 8)
- [x] Evidence Audit appendix is present and maps each key finding to its evidence status (Appendix D)
- [x] Commercial readiness is stated as "NOT EVALUATED" unless confirmed adoption evidence exists (Section 6.6); adoption absence labeled NOT OBSERVED, not CONFIRMED ABSENT, with coverage stated
- [x] Decision matrix output is included, showing the reasoning path (motivation object → expected-success → causal bridge test → mechanism/design-choice distance), the Causal Bridge Test with bridge_status, and the structured obviousness evidence object (Sections 9 and 4.6)
- [x] **Conclusion is per-gate only — no scalar "overall patentability" label and no "Overall patentability" row in the default output** (§9.2); executive score appears only as a derived-on-request summary (§9.3)
- [x] **Every NOT OBSERVED / NOT IDENTIFIED finding carries its coverage object**; no finding is upgraded toward CONFIRMED ABSENT; no bounded universe was claimed (Appendix D, Section 8)
- [x] **C/D distances reported per reference pathway, never combined**: C2/D3 vs US424,036; C3/D3 vs US416,195 (§4.6–4.7)
- [x] **Motivation Object present with categorized source lists and deterministic derivation**: PARTIALLY GROUNDED (analogous only) (§4.6.3)
- [x] **Knowledge decomposition present**: component/principle/function CONFIRMED PRESENT; combination/application NOT OBSERVED (§4.6.1–4.6.2)
- [x] No exclusivity framing survives: "only partner" / "no commercial vehicle" replaced with "strongest identified pathway" (§7.1)
- [x] Forward-citation counts relabeled as a neutral historical signal, not patentability evidence (§3.7, §4.6)
- [x] Claim-construction layer is clearly labeled as based on the patent's actual claims (not a provisional construct — formal claims exist in this case)
- [x] Newly identified prior art (US424,036) is integrated into the claim-element mapping rather than ignored; the earlier report's incomplete mapping is explicitly corrected (§1.3)

---

*End of Report*
*Generated by the Invention Evaluation Framework v1.5 — full 9-stage pipeline execution with live searches; v1.5 constructs exercised: Causal Bridge Test, mechanism/design-choice distance (C/D), Negative Evidence Coverage Rule, first-class Motivation Object, knowledge decomposition, per-gate-only conclusion*
*This report is NOT legal advice. All patentability assessments are preliminary. Consult qualified patent counsel for formal opinions.*
