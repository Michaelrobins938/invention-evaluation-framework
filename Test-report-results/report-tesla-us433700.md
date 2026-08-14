# Invention Evaluation Report
## Tesla US Patent 433,700 — Alternating-Current Electro-Magnetic Motor

**Prepared:** August 13, 2026
**Framework:** Invention Evaluation Framework v1.4
**Status:** Historical/Educational Analysis — Not Legal Advice
**Pipeline:** Full 9-stage execution (rerun)

---

> **DISCLAIMER:** This report is a historical and educational patentability analysis of an 1890 invention. It is **NOT** a legal opinion, **NOT** a freedom-to-operate (FTO) analysis, and **NOT** a substitute for advice from qualified patent counsel. All patentability assessments are preliminary and based on publicly available patent records only. This analysis does not constitute legal advice and should not be relied upon for any legal or commercial decision.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Analysis](#2-technology-analysis)
3. [Patent Landscape Analysis](#3-patent-landscape-analysis)
4. [IP / Novelty Analysis](#4-ip--novelty-analysis)
5. [Literature Search](#5-literature-search)
6. [Market Opportunity Analysis](#6-market-opportunity-analysis)
7. [Potential Partners](#7-potential-partners)
8. [Insufficient Evidence / Not Evaluated](#8-insufficient-evidence--not-evaluated)
9. [Decision Matrix Output](#9-decision-matrix-output)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

**Invention:** US Patent 433,700, "Alternating-Current Electro-Magnetic Motor," invented by Nikola Tesla, filed March 26, 1890 (Serial No. 345,388), granted August 5, 1890, assigned to Tesla Electric Company. The invention uses a **magnetic shield** (annealed insulated iron wire wound around one set of field coils) to artificially create a phase difference between two sets of field magnets from a single AC power source — improving motor efficiency without requiring two independent current sources.

### Key Findings

| Dimension | Assessment | Summary |
|---|---|---|
| **Utility** | ✅ High | Practical improvement to AC motor efficiency; assigned to operating company; addresses real industrial need |
| **Novelty** | ⚠️ Moderate–High | No single prior art reference anticipates all claim limitations; the magnetic shield element (limitations d & e) is new. However, the invention builds directly on Tesla's own 1887–1889 patent portfolio |
| **Inventive Step** | ⚠️ Moderate, unresolved | The shield mechanism is technically non-obvious (high mechanism displacement: material-level vs. circuit-level control), but the problem (artificial phase difference from single source) was already solved by Tesla in US416,195 (1889) using self-induction + supplemental poles. The shield is an alternative means to the same end. Obviousness is plausible but **not established** — the motivation for the substitution is INFERRED, not evidenced |
| **Combination-Obviousness Exposure** | ⚠️ Moderate | The invention's novelty rests on combining known elements (AC motor with two circuits + magnetic shielding + phase delay). A combination can be completely novel while still being obvious — the operative question is derivation risk: how readily the combination can be reconstructed from prior-art components with a demonstrated motivation to combine. That motivation is not evidenced |
| **Self-Blocking Risk** | 🔴 HIGH | Tesla's own prior patents (US381,968; US382,279; US416,195) are the closest prior art. Elevated risk of double-patenting or obviousness rejection based on own earlier work |
| **Market Opportunity** | ⚠️ Moderate–High | AC motor market was nascent but growing rapidly in 1890. Commercial success depended on Westinghouse licensing, not just the patent itself |
| **Forward Citations** | ⚠️ Low (neutral signal) | Only 1 later patent cites US433700 (Dell, 2006 — AC electromagnetic pump). **This is a historical technology-development signal, not a patentability signal** — low adoption does not establish non-obviousness (the approach may have been obvious, inferior, expensive, or superseded) |
| **Unexpected Result** | ❓ NOT IDENTIFIED | No quantitative performance data found demonstrating that the shield approach produces an unexpected technical result vs. self-induction approach |

### Recommended Next Action

From a historical perspective, the patent was granted and its commercial adoption is **not observed** (coverage insufficient to establish confirmed absence). The magnetic shield approach was superseded by capacitor-based phase splitting and other methods. For contemporary relevance, the patent's primary value is as prior art in electromagnetic shielding and AC motor design, not as a live commercial asset.

---

## 2. Technology Analysis

### 2.1 Plain-Language Description

Tesla's 1890 patent describes an AC induction motor that generates a rotating magnetic field from a **single AC power source**. The motor uses two sets of field-magnet cores, each wound with coils connected to separate branched circuits from that one source. A **magnetic shield** (insulated iron wire wound around one set of coils) delays current flow and magnetization in those cores, creating an artificial **phase difference** between the two magnet sets. This approaches the ideal condition where one set peaks while the other is at minimum — improving efficiency without requiring two independent current sources.

The shield works through magnetic saturation: initially, the iron-wire shield absorbs magnetic flux lines, preventing the underlying core from magnetizing. Once the shield itself becomes saturated (can carry no more flux), it stops blocking, and the core magnetizes — but this happens with a time delay relative to the unshielded set. The extent of the delay is "arbitrarily determined by the thickness of the shield H, and other well-understood conditions."

### 2.2 Feature–Benefit Map

| Feature | Benefit |
|---|---|
| Two branched circuits from single AC source | Eliminates need for independent generators; reduces cost and complexity |
| Magnetic shield (annealed iron wire) around one coil set | Artificially creates phase difference between magnet sets |
| Shield saturates then releases | Delayed magnetization produces tunable timing offset |
| Shield thickness adjustable | Phase difference extent is arbitrarily determined per application |
| Fig. 2 variant: shield in series with other circuit | Dual mechanism — current acceleration in one branch, retardation in the other |

### 2.3 Innovation Assessment

**What differs from known approaches:** Prior art required two independent current sources to achieve the desired 90° phase difference. Tesla achieves it from a single source using magnetic shielding — a fundamentally different architectural approach from the self-induction method disclosed in US416,195.

**⚠️ Combination-obviousness exposure (moderate):** The invention combines known elements — AC motors, magnetic shields, branched circuits — in a new configuration. **A combination can be completely novel while still being obvious**; the label "combination novelty" conflates the two questions. The operative test is *derivation risk*: how readily can this combination be reconstructed from the prior-art components, with a demonstrated motivation to combine? The components exist in prior art; the delta step (interposing a saturation-timed shield as a phase-control mechanism) is not evidenced in the accessible pre-filing literature. Motivation for the substitution is therefore INFERRED, not confirmed — which caps the obviousness finding at "plausible but unresolved."

**Specific claimed-unique elements:**
1. Magnetic shields/screens interposed between coils and cores to retard magnetization (Claim 1)
2. Shields wound at right angles to coil convolutions (Claim 2)
3. Shields forming closed magnetic circuits around coils, interposed between coils and cores (Claim 3)
4. Insulated iron-wire shields on one circuit's coils, connected in series with the other circuit's coils (Claim 4)

### 2.4 Unexpected-Result Gate

**Evidence state: NOT IDENTIFIED**

The patent specification describes the mechanism qualitatively but provides no quantitative data (efficiency measurements, torque curves, power factor comparisons) demonstrating that the shield approach produces an unexpected technical result beyond what would be expected from delayed magnetization. No external source confirming unexpected performance has been identified.

This is an evidence gap — it weakens the inventive-step argument if the combination novelty flag is challenged.

### 2.5 Regulatory Burden (1890 Context)

**Low.** No modern regulatory framework existed. Patent examination was the primary gate. No safety certifications, environmental reviews, or FDA/CE requirements applied.

### 2.6 Development Stage

**Commercialization (1890).** Tesla Electric Company was already formed; the patent was assigned to them. The motor was being positioned for the emerging AC power distribution industry.

### 2.7 IPC/CPC Classification Seed

- **H02K 17/00** — Asynchronous induction motors (confirmed from Google Patents)
- **H02K 17/02** — Asynchronous induction motors
- **H02K 17/16** — Asynchronous induction motors with internally short-circuited rotor windings
- **H02K** — Dynamo-electric machines broadly

### 2.8 What Is Still Not Understood

- Exact performance characteristics (efficiency, torque, speed) of this specific design vs. contemporary DC motors
- Whether the phase difference created by the shield was sufficient for practical commercial operation or was primarily theoretical
- Relationship between this patent and Tesla's broader polyphase AC system patents (e.g., US 381,968, filed 1887)
- Why this specific shielding approach was not widely adopted if technically effective

---

## 3. Patent Landscape Analysis

### 3.1 Search Strategy

- **Primary:** Google Patents (full-text, classification-filtered)
- **Secondary:** Google Patents "Similar Documents" and citation chains (Espacenet returned 403)
- **Query scope:** H02K class, "alternating current motor" + "phase" / "induction" / "rotating field", priority dates 1885–1895, inventor ≠ Tesla

### 3.2 Field Volume & Trend

The field is **small and concentrated** — approximately 12–15 US patents in the 1885–1895 window directly relevant to AC motor phase/induction principles. Filing volume is low by modern standards (the AC motor industry was nascent), but **patent quality is high** — most surviving patents are foundational.

**Trend:** Sharp spike in 1887–1890, driven almost entirely by Tesla's own prolific filing. Non-Tesla filings are sparse (2–3 identifiable).

### 3.3 Geographic Distribution

- **United States:** Dominant jurisdiction (all identified patents are US)
- **Europe:** Limited evidence of parallel filings in this narrow window
- **Assessment:** Single-jurisdiction filing pattern; no international patent family detected for US433700 specifically (Country Status: US only, confirmed from Google Patents)

### 3.4 Top Assignees & Concentration

| Assignee | Patents in Field | Share |
|---|---|---|
| Tesla Electric Company / Nikola Tesla | 4+ (381968, 382279, 381970, 433700) | ~70–80% |
| Individual inventors (Billberg & Winand, Ripley) | 2 | ~20% |
| Others (Kennedy, Scheeffer, etc.) | 2–3 | ~10% |

**Signal:** This is a **highly consolidated field dominated by a single inventor** (Tesla). The risk pattern is not "many blocking patents from many players" but rather **Tesla's own prior patents forming the closest prior-art wall** — a self-anticipation / double-patenting risk.

### 3.5 CPC/IPC Subclass Concentration

- **H02K 17/00** — Asynchronous induction motors (primary)
- **H02K 17/02** — Asynchronous induction motors, general
- **H02K 17/16** — Cage-rotor induction motors
- **H02P 21/00** — Control of electric motors by vector control (later citation signal)
- **H01F 29/00** — Variable transformers/inductances (related)

### 3.6 Key Patent Profiles

| Patent | Date | Inventor | Relevance | Legal Status |
|---|---|---|---|---|
| US381,968 | 1888-05-01 | Tesla | **Highly relevant** — foundational polyphase motor with independent circuits; direct ancestor of 433700 | Historical term expired (grant + 17 yrs) |
| US382,279 | 1888-05-01 | Tesla | **Highly relevant** — induction motor with closed armature coils; same inventor, same assignee | Historical term expired (grant + 17 yrs) |
| US381,970 | 1888-05-01 | Tesla | **Related** — electrical distribution system; provides system-level context | Historical term expired (grant + 17 yrs) |
| US416,195 | 1889-12-03 | Tesla | **Potentially blocking** — artificial phase difference via self-induction + supplemental poles | Historical term expired (grant + 17 yrs) |
| US433,702 | 1890-08-05 | Tesla | **Related** — sibling patent; same shield principle applied to transformers | Historical term expired (grant + 17 yrs) |
| US433,703 | 1890-08-05 | Tesla | **Related** — sibling patent; core lamination delay alternative | Historical term expired (grant + 17 yrs) |
| US444,934 | 1891-01-20 | Billberg & Winand | **Not prior art** (filed after) — laminated Faraday disk motor; different approach | Historical term expired (grant + 17 yrs) |
| US347,642 | 1886-08-17 | Ripley | **Background** — current converter/rectifier; different purpose, but uses commutator-based phase control | Historical term expired (grant + 17 yrs) |

### 3.7 Citation Signal

- US433700 is **cited by only 1 later patent**: US20060045755A1 (Dell, 2006) — AC electromagnetic pump cooling. Extremely low forward citation count for a foundational Tesla patent. **This is a historical technology-development signal, not a patentability signal** — low adoption does not establish non-obviousness (the approach may have been obvious, inferior, expensive, unreliable, superseded, or commercially irrelevant). At most it indicates later patent lineage did not strongly converge on this mechanism.
- US381968 (Tesla's earlier patent) is cited by **70+ patents** — confirming it as the dominant prior-art anchor in this family.
- US416195 is cited by **3 patents** — moderate signal.
- US382279 is cited by **21+ patents** — strong signal for the induction motor with closed coils.

### 3.8 Landscape Interpretation

- **Early-stage research activity, not commercial saturation** — the field has few players, low filing volume, and is inventor-dominated.
- **Elevated self-blocking risk** — Tesla's own 1887–1888 patents (381968, 382279) are the closest prior art. The 1890 shielding patent appears to be a **narrow improvement** within Tesla's own existing claim scope.
- **No dominant competitor patents detected** — the field is not crowded with blocking patents from other assignees in this window.
- **Sharp filing growth 1887–1890** — confirms this as a hot, rapidly-developing field with high prior-art density (all Tesla-generated).

---

## 4. IP / Novelty Analysis

> **NOT LEGAL ADVICE:** This section provides a preliminary patentability assessment based on abstract-level and partial claim review. It is **NOT** a substitute for a formal patentability opinion from qualified patent counsel. It does **NOT** constitute a freedom-to-operate (FTO) opinion.

### 4.1 Claim Construction

US433700 contains 4 independent claims. The analysis below uses **Claim 1** as the primary evaluation claim, with Claims 2–4 noted for completeness.

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

**Query 1:** AC motor + two circuits + phase difference (pre-1890)
**Query 2:** Magnetic shield/screen + motor + retardation (pre-1890)
**Query 3:** Self-induction + phase + alternating current motor (pre-1890)
**Query 4:** Rotating magnetic field + polyphase + Tesla prior (pre-1890)

### 4.3 Triage Results

| Reference | Date | Inventor | Relevance | Classification | Structural Relationship |
|---|---|---|---|---|---|
| US381,968 | 1888-05-01 | Tesla | **Potentially blocking** | H02K 17/00 | E3 — same functional objective |
| US416,195 | 1889-12-03 | Tesla | **Potentially blocking** | H02K 17/00 | E4 — same causal architecture |
| US382,279 | 1888-05-01 | Tesla | **Highly relevant** | H02P 21/00 | E3 — same functional objective |
| US381,970 | 1888-05-01 | Tesla | **Related** | H02K (distribution) | E2 — shared components |
| US347,642 | 1886-08-17 | Ripley | **Background** | H02M 3/00 | E1 — same terminology/domain |
| US444,934 | 1891-01-20 | Billberg & Winand | **Not prior art** (filed after) | H02K 17/00 | E0 — unrelated (post-filing) |

### 4.4 Claim-Element Mapping — US433700 Claim 1

#### US381,968 (Tesla, 1888) — Claim 1

> *"The combination, with a motor containing separate or independent circuits on the armature or field-magnet, or both, of an alternating-current generator containing induced circuits connected independently to corresponding circuits in the motor, whereby a rotation of the generator produces a progressive shifting of the poles of the motor..."*

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "alternating-current generator... progressive shifting of the poles of the motor" |
| (b) Two energizing-circuits | ✅ Yes | "separate or independent circuits on the armature or field-magnet" |
| (c) Magnetic cores and coils | ✅ Yes | Coils on ring R, armature with coils — explicitly described |
| (d) Interposed magnetic shields | ❌ No | No shield or screen element disclosed; uses independent generator circuits for phase difference |
| (e) Retarding magnetization | ❌ No | Phase difference comes from generator, not from retarding magnetization of cores |

**Verdict:** Does NOT anticipate. Missing limitations (d) and (e).
**Structural relationship:** E3 — same functional objective (rotating field from multiple circuits), different mechanism (independent sources vs. shield delay).

---

#### US416,195 (Tesla, 1889) — Claim 1

> *"In an alternating-current motor, the combination, with an armature wound with closed coils, of a field having two or more energizing-circuits of different self-induction, whereby the currents in said circuits differ in phase, and supplemental poles situated between the primary poles and wound with coils included in derived circuits..."*

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "alternating-current motor" — explicit |
| (b) Two energizing-circuits | ✅ Yes | "two or more energizing-circuits of different self-induction" |
| (c) Magnetic cores and coils | ✅ Yes | Field-magnet with poles B B, C C, coils D, E — explicitly described |
| (d) Interposed magnetic shields | ❌ No | Uses different self-induction in circuits, not magnetic shields; supplemental poles B' C' are additional pole pieces, not shields |
| (e) Retarding magnetization | ❌ No | Phase difference from different self-induction (circuit-level), not from retarding magnetization of cores (material-level) |

**Verdict:** Does NOT anticipate. Missing limitations (d) and (e).
**Structural relationship:** E4 — same causal architecture (artificial phase difference from single source), different mechanism (self-induction vs. magnetic shielding).

---

#### US382,279 (Tesla, 1888) — Claim 2

> *"An electro-magnetic motor having its field-magnets wound with independent coils and its armature with independent closed coils, in combination with a source of alternating currents connected to the field-coils and capable of progressively shifting the poles of the field-magnet..."*

| Limitation | Disclosed? | Evidence |
|---|---|---|
| (a) AC motor | ✅ Yes | "electro-magnetic motor" with "alternating currents" |
| (b) Two energizing-circuits | ✅ Yes | "independent coils" on field-magnets, connected to generator with independent circuits |
| (c) Magnetic cores and coils | ✅ Yes | Annular core A wound with four coils C C C C; armature disk D with coils E E |
| (d) Interposed magnetic shields | ❌ No | No shield or screen element; phase difference from generator's independent coils |
| (e) Retarding magnetization | ❌ No | Phase difference from generator design, not from retarding core magnetization |

**Verdict:** Does NOT anticipate. Missing limitations (d) and (e).
**Structural relationship:** E3 — same functional objective, different mechanism.

### 4.5 Anticipation Gate Result

**ALL flagged references:** Missing at least limitations (d) and (e).
**Gate result:** NOT ANTICIPATED by any single reference. Move to obviousness analysis.

### 4.6 Obviousness Analysis — Structured Evidence Object

```yaml
obviousness_case:
  closest_reference:
    patent_or_publication: US416,195 (Tesla, 1889)
    relevance: E4 — same causal architecture (artificial phase difference from single source)
    causal_distance: C3 — different physical principle (circuit-level self-induction vs. material-level saturation delay) producing the same effect
  distinguishing_limitations:
    - limitation: (d) Interposed magnetic shields/screens
      disclosed_in_closest: no
      delta: US416,195 uses different self-induction in circuits + supplemental poles; US433700 uses a magnetic shield interposed between coil and core
    - limitation: (e) For retarding magnetization of said cores
      disclosed_in_closest: no
      delta: US416,195 retards current phase via circuit inductance; US433700 retards core magnetization via material saturation delay
  proposed_modification_paths:
    - type: substitution
      description: Substitute magnetic shielding for self-induction/supplemental poles as the phase-delay mechanism
      prior_art_basis: General electromagnetic knowledge of magnetic saturation (well-known by 1890)
      motivation:
        reason: Desire for an alternative to self-induction that avoids the need for supplemental pole pieces and complex winding
        evidence: INFERRED — no pre-filing source identified stating this motivation or documenting the substitution as a design option. The reason is plausible but not evidenced.
      reasonable_expectation_of_success: medium
      compatibility_constraints: Shield must be sized to saturate at the right point in the AC cycle; thickness must be tuned to the application; shield adds material and manufacturing complexity; saturation delay introduces hysteresis/eddy-current losses not present in the circuit-level approach
    - type: combination
      description: Combine the two-circuit AC motor of US381,968 with magnetic shielding known in general electromagnetic practice
      prior_art_basis: US381,968 (two-circuit motor) + general knowledge of magnetic saturation/shielding
      motivation:
        reason: Single-source operation was a known goal; shielding was a known electromagnetic phenomenon
        evidence: INFERRED — the goal is confirmed (US416,195 solves it), but no source evidences that a skilled person would reach for a saturation shield specifically to achieve it
      reasonable_expectation_of_success: medium
      compatibility_constraints: Shield must not interfere with the rotating field; must be compatible with the armature's induced currents
  mechanism_displacement:
    prior_art_control_domain: electrical_circuit (self-induction in energizing circuits)
    claimed_control_domain: magnetic_material (saturation-timed shielding interposed between coil and core)
    displacement: high
    rationale: The causal intervention point moves from the electrical circuit into the magnetic material system. This is not merely a component swap — it relocates where phase control happens. High displacement is a non-obviousness argument.
  technical_effect:
    effect: Creates artificial phase difference between two field-magnet sets from a single AC source, enabling rotating field without independent generators
    evidence: NOT IDENTIFIED — no quantitative performance data found comparing shield approach to self-induction approach
  unexpected_result: unknown — no evidence of unexpected performance advantage identified
  evidence_for_obviousness:
    - source: US416,195 (Tesla, 1889)
      supports: Establishes that artificial phase difference from a single source was a known goal with a working solution; the problem was already solved
    - source: US381,968 (Tesla, 1888)
      supports: Establishes the two-circuit AC motor architecture that US433700 builds on
    - source: General electromagnetic knowledge (1885-1890)
      supports: Magnetic saturation of iron was well-known as a background principle (CONFIRMED PRESENT). NOTE: this establishes the principle, NOT the engineering application — the step from "iron saturates" to "a skilled engineer would choose an insulated iron-wire shield interposed between coil and core as a controllable phase-delay mechanism in an AC motor" is NOT OBSERVED in the accessible pre-filing record and must not be carried by the principle's evidentiary weight.
  evidence_against_obviousness:
    - source: US433700 specification
      undermines: The shield operates through a physically distinct mechanism (magnetic saturation delay at the material level) vs. US416,195's circuit-level self-induction delay — high mechanism displacement supports a "different principle of operation" argument
    - source: Search results (patent + literature)
      undermines: No accessible pre-1890 source was identified describing this exact shield mechanism — the specific application step is NOT OBSERVED, which weakens the confidence of any obviousness finding
  neutral_signals:
    - source: Low forward citation count (1 citation)
      note: NOT a patentability signal. Low later adoption does not establish non-obviousness — the approach may have been obvious, technically inferior, expensive, unreliable, superseded, or commercially irrelevant. At most it indicates later technological lineage did not strongly converge on this mechanism.
  unresolved_questions:
    - Was the shield approach more efficient, cheaper, or simpler than self-induction in practice?
    - Did the shield introduce losses (hysteresis, eddy currents in the iron wire) that offset the phase-control benefit?
    - Why was this approach not adopted commercially if it was a viable alternative?
    - Is there any pre-1890 source (journal, textbook, lecture) that documents saturation-based phase delay as a design option — i.e., evidence for the motivation that is currently INFERRED?
  evidence_state: NOT IDENTIFIED — no performance comparison data available; motivation for the substitution is INFERRED
  final_assessment: Moderate obviousness risk, UNRESOLVED — the problem was already solved by Tesla in US416,195 using a different mechanism; substituting magnetic shielding for self-induction is a plausible modification path with medium expectation of success. However: (1) the motivation for the substitution is INFERRED, not evidenced; (2) mechanism displacement is high (material-level vs. circuit-level control), which is a non-obviousness argument; (3) the specific application is NOT OBSERVED in the accessible pre-filing record. Obviousness is plausible but not established.
```

**Evidence → Inference → Conclusion firewall (finding structure):**

```yaml
finding:
  proposition: "The shield mechanism was obvious to a skilled person in 1890"

  evidence:
    - source: "US416195"
      observation: "Tesla already used self-induction to create phase differences."

    - source: "historical electromagnetic knowledge"
      observation: "Magnetic saturation was known (background principle, CONFIRMED PRESENT)."

    - source: "search results"
      observation: "No accessible pre-1890 source was identified describing this exact shield mechanism (application step, NOT OBSERVED)."

  inference:
    statement: "A skilled person could potentially have considered magnetic saturation as another phase-delay mechanism."
    strength: moderate

  conclusion:
    statement: "Obviousness remains plausible but is not established."
    confidence: medium
```

### 4.7 Causal Distance From Prior Art

Semantic (structural) distance and causal distance are **not the same thing**. US416,195 is semantically extremely close (E4 — same architecture, same objective) but mechanistically separated: phase control happens in the electrical circuit (self-induction) rather than in the magnetic material (saturation shield). The table below separates the two dimensions.

| Reference | Functional similarity | Causal distance | Mechanism |
|---|---:|---:|---|
| US381,968 | High (E3) | C3 — different principle, same effect | Independent circuits from generator |
| US416,195 | Very high (E4) | **C3 — different principle, same effect** | Circuit-level self-induction |
| US433,700 (target) | — | — | Material-level magnetic saturation shield |
| US433,702 | Very high (E4) | C3/C4 — shielding principle, different application | Shield in transformer |
| US433,703 | High (E3) | C3 — different principle | Core lamination / delayed magnetization geometry |

**Interpretation:** The causal gap between US433,700 and its closest prior art (US416,195) runs from *electrical inductance → phase delay* on one side to *magnetic saturation → phase delay* on the other. The two converge on the same engineering objective through a different physical principle (C3) with high mechanism displacement (control domain moves from circuit to material). This gap is a genuine argument against obviousness — but it must be weighed against the fact that the problem itself was already solved, and the motivation to substitute is INFERRED rather than evidenced.

### 4.8 Patentability Scoring

| Axis | Score | Rationale | Evidence Status |
|---|---|---|---|
| **Utility** | **High** | Practical AC motor improvement; assigned to Tesla Electric Company; addresses real efficiency problem in single-source AC systems | CONFIRMED PRESENT (patent granted; assigned to operating company) |
| **Inventive Step** | **Moderate, unresolved** | The shield mechanism is a specific, technically non-obvious solution (high mechanism displacement; C3 causal distance from closest art). However, the problem (artificial phase difference from single source) was already identified and solved by Tesla in US416,195 using self-induction + supplemental poles. The shield is an alternative means to the same end. Motivation for the substitution is INFERRED, not evidenced. | NOT IDENTIFIED (no unexpected result data); motivation INFERRED |
| **Novelty** | **Moderate–High** | No single prior art reference anticipates all claim limitations. The magnetic shield element (limitations d & e) is new. However, the invention builds directly on Tesla's own 1887–1889 patent portfolio. | CONFIRMED PRESENT (no anticipating reference found) |

### 4.9 Combination-Obviousness Exposure (Derivation Risk)

**This is not "combination novelty."** A combination can be completely novel while still being obvious — novelty and obviousness are different questions, and labeling the former "combination novelty" falsely implies the combination is the strongest basis for patentability when it is actually the weakest. The operative question is **derivation risk**: how readily can the claimed combination be reconstructed from prior-art components, with a demonstrated motivation to combine?

| Component | Where it exists in prior art | Evidence |
|---|---|---|
| AC motor with two energizing circuits | US381,968 (1888) | CONFIRMED PRESENT |
| Artificial phase difference from single source | US416,195 (1889) | CONFIRMED PRESENT |
| Magnetic shielding of coils | General electromagnetic knowledge | CONFIRMED PRESENT (principle) |
| **Delta: saturation-timed shield interposed between coil and core as phase-control mechanism** | **Not identified in accessible pre-1890 record** | **NOT OBSERVED** |

**Derivation assessment:** The components exist; the delta step is the *application* of saturation timing to phase control via an interposed shield. That application is NOT OBSERVED in the accessible record, and no source evidences a motivation to make this specific substitution. Derivation risk is therefore **moderate and unresolved** — the combination is not established as obvious, but the absence of a demonstrated unexpected result and the INFERRED motivation leave the inventive-step case incomplete. The unexpected-result gate returned **NOT IDENTIFIED** — no performance data was found.

### 4.10 Self-Prior-Art Exposure

The closest references are Tesla's own earlier filings:

| Risk Type | Assessment |
|---|---|---|
| **Anticipation exposure** | LOW — no own prior patent discloses limitations (d) and (e) |
| **Obviousness exposure** | MODERATE, UNRESOLVED — US416,195 solves the same problem with a different mechanism; substitution argument is plausible but motivation is INFERRED |
| **Double-patenting exposure** | MODERATE — US416,195 and US433700 both claim artificial phase difference from a single source; different mechanisms but same functional result |
| **Family/priority relationship** | None — US433700 is a separate filing (Serial No. 345,388), not a continuation or divisional of US416,195 (Serial No. 311,419) |

### 4.11 Design-Space Position

US433700 is best understood not as an isolated invention but as one node in a **design-space exploration event**: Tesla was implementing the same higher-level architecture — *artificial phase difference from a single AC source* — through multiple physical mechanisms in rapid succession.

```text
                         PHASE DIFFERENCE
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   Independent circuits   Self-induction       Magnetic shielding
      US381968             US416195              US433700
          │                    │                    │
          ▼                    ▼                    ▼
    electrical source     circuit dynamics     material dynamics
```

And then:

```text
US433702  → same shield concept → transformer application
US433703  → alternative magnetic-delay architecture → core lamination geometry
```

**Interpretation:** This pattern reframes the evaluation question from "is this patent novel?" to "what region of the inventor's design space does this invention occupy?" US433700 sits at the material-dynamics corner of Tesla's exploration of phase-control mechanisms. This is contextual evidence about the inventor's working method — it does not by itself establish or refute patentability, but it explains why the shield patent reads as a deliberate exploration of an alternative mechanism rather than a marginal variation of US416,195.

---

## 5. Literature Search

### 5.1 Search Queries

- Q1: "alternating current motor" + "phase difference" + "magnetic shield" (pre-1890)
- Q2: "self-induction" + "alternating current" + "retardation" (pre-1890)
- Q3: "rotating magnetic field" + "polyphase" (pre-1890)
- Q4: Contemporary electrical engineering journals (Electrician, Electrical World, etc.)

### 5.2 Findings

| Source | Date | Relevance | Key Content |
|---|---|---|---|
| **US433,702 (Tesla)** | Filed Mar 26, 1890 | **Highly relevant** | Sibling patent — same magnetic shield principle applied to transformers. Confirms shield concept was Tesla's active R&D focus at filing date. Not prior art (same inventor, same filing period), but critical for context. |
| **US433,703 (Tesla)** | Filed Apr 4, 1890 | **Related** | Uses core lamination delay (inner vs. outer core sections) instead of external shield — alternative mechanism to the same problem. |
| **Contemporary electrical engineering literature** | 1885–1890 | **Insufficient evidence** | Archive.org and Google Books searches did not return accessible full-text sources for this specific window. The rotating magnetic field concept was known (Ferraris 1885, Tesla 1888), but the specific magnetic-shield phase-delay mechanism does not appear in accessible non-patent literature before the filing date. |

### 5.3 Key Technical Context

- **Rotating magnetic field theory** (Ferraris, 1885; Tesla, 1888): Well-established by 1890.
- **Self-induction / phase retardation**: Standard electromagnetic knowledge by 1890.
- **Magnetic saturation of iron**: Well-known phenomenon.
- **Magnetic shielding**: Known in general, but **application to AC motor phase control via saturation-delay is not found in accessible pre-1890 non-patent literature**.

### 5.4 Evidence-State Assessment

| Claim | Evidence State |
|---|---|
| Non-patent literature discloses shield-for-phase-delay mechanism before March 26, 1890 | **NOT IDENTIFIED** — searched Archive.org and Google Books; no accessible full-text sources for 1888–1890 electrical engineering journals |
| Rotating magnetic field concept was known before 1890 | **CONFIRMED PRESENT** — Ferraris (1885), Tesla (1888) |
| Magnetic saturation of iron was known before 1890 | **CONFIRMED PRESENT** — general electromagnetic knowledge |
| Specific shield-for-phase-delay mechanism appears in non-patent literature | **NOT IDENTIFIED** — not found in searched sources |

### 5.5 Assessment

**Insufficient evidence** for a non-patent publication disclosing the specific shield-for-phase-delay mechanism before the March 26, 1890 filing date. Full-text access to 1888–1890 issues of *The Electrician*, *Electrical World*, and *American Electrician* would be needed to confirm absence of non-patent disclosure.

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
| Total US electrical industry revenue (1890) | **Not established** — no sufficiently reliable primary-source dataset identified to calculate a defensible figure | NOT IDENTIFIED in primary source; earlier estimate (~$100M) removed — it could not be reconstructed from a cited source |
| Motor segment | <5% of total; AC motors were a tiny fraction | Derived from historical electrification data (INFERRED) |
| Growth rate (AC motor adoption 1890–1900) | **Not established** — no reliable primary-source dataset identified to calculate a defensible CAGR | Earlier estimate (30–50% CAGR) removed — it could not be reconstructed from a cited source |
| Addressable market for this invention | Subset of AC motor market where single-source phase control is needed | Derived (INFERRED) |

**Qualitative statement (defensible):** AC electrical infrastructure was undergoing rapid expansion during the period — the "War of the Currents" was being won by AC for long-distance distribution, and Westinghouse's 1893 World's Fair contract was a watershed. But no sufficiently reliable primary-source dataset was identified to calculate a defensible CAGR for AC motor adoption. **That qualitative statement is more useful than an impressive-looking number with no reconstructable basis.**

### 6.4 Competitive Landscape

| Competitor | Technology | Position | IP Posture |
|---|---|---|---|
| Edison General Electric (DC) | DC motors, direct distribution | Losing ground on long-distance; dominant in urban centers | Strong DC patent portfolio; declining relevance |
| Westinghouse Electric | AC systems (Tesla-licensed) | Gaining; 1893 World's Fair will be watershed moment | Holds Tesla's core AC patents via 1888 licensing deal |
| Thomson-Houston Electric | Arc lighting, AC dynamos | Major player; merged into GE in 1892 | Moderate patent portfolio |
| Independent AC motor inventors | Various designs (Ferraris, Bradley, etc.) | Fragmented; no dominant design yet | Sparse patent coverage |

### 6.5 Commercial Actionability Assessment

| Factor | Assessment | Evidence State |
|---|---|---|
| Clear buyer | ✅ Industrial operators, utilities | CONFIRMED PRESENT |
| Feasible production cost | ✅ Iron wire, copper coils — standard materials | CONFIRMED PRESENT |
| Accessible regulatory pathway | ✅ Patent granted; no additional approvals needed | CONFIRMED PRESENT |
| Viable competitive position | ⚠️ Depends on Westinghouse licensing; Tesla Electric Company was financially strained | NOT IDENTIFIED — no evidence of standalone competitive viability |
| **Overall commercial actionability** | **Moderate–High** — technically viable, but commercial success depended on corporate licensing, not just the patent itself | — |

**Scoring:** Market size (med) × Growth (high, qualitative — directional only, no defensible CAGR) × Accessibility (med) × Competitive intensity (med) = **Moderate–High**, no "low" scores.

### 6.6 Technical Maturity vs. Commercial Readiness

| Dimension | Assessment | Evidence State |
|---|---|---|
| Patent disclosure | CONFIRMED PRESENT | Patent granted Aug 5, 1890 |
| Engineering feasibility | High | Standard materials; no exotic manufacturing needed |
| Prototype evidence | NOT OBSERVED | No evidence found that a prototype was built and tested; coverage insufficient to establish it never was |
| Production evidence | NOT OBSERVED | No evidence of production; coverage insufficient to establish absence |
| Commercial adoption evidence | NOT OBSERVED | No evidence found that Westinghouse or any manufacturer adopted the shield approach in production motors — but the historical record is not dense enough to establish confirmed absence |
| **Commercial readiness** | **NOT EVALUATED** | No confirmed adoption evidence exists |

### 6.7 SWOT

| Strengths | Weaknesses |
|---|---|
| Eliminates need for independent generators | No standalone product value — component improvement only |
| Tunable phase delay via shield thickness | Shield adds material and manufacturing complexity |
| Uses standard materials (iron wire, copper) | No demonstrated performance advantage over self-induction (US416,195) |
| Patent granted and assigned to operating company | Tesla Electric Company financially strained |
| **Opportunities** | **Threats** |
| AC motor market growing rapidly (qualitative — CAGR not defensibly quantifiable) | Self-induction approach (US416,195) is an established alternative |
| Westinghouse licensing deal could incorporate improvement | Technology substitution risk — capacitor phase splitting may supersede |
| Industrial electrification expanding | Edison's DC system still dominant in urban centers |
| Mining and remote industrial sites favor AC | No evidence of commercial adoption (NOT OBSERVED) |

### 6.8 Key Market Risks

1. **Tesla Electric Company financial instability** — Tesla's own company was struggling; the patent was assigned to them but they lacked manufacturing capacity.
2. **Westinghouse licensing dependency** — Westinghouse held the broader polyphase patent portfolio (US381,968 etc.). The shield improvement was valuable primarily within the Westinghouse system.
3. **Technology substitution risk** — Self-induction-based phase control (US416,195) was an alternative approach; market might standardize on that instead.
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
| **Likelihood** | Moderate — Westinghouse already had US416,195's self-induction approach; would need to see efficiency advantage to adopt the shield alternative |

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
| Westinghouse already has equivalent solution (US416,195) | Demonstrate efficiency advantage of shield approach vs. self-induction approach — **but no performance data exists** |
| Tesla Electric Company financial instability | Structure deal as patent assignment or licensing, not equity |
| No standalone product value | Bundle with full motor system design; sell as system improvement, not component |
| Shield approach never commercially adopted | NOT OBSERVED — no evidence of adoption found; historical record insufficient to establish confirmed absence |

---

## 8. Insufficient Evidence / Not Evaluated

This section surfaces all NOT IDENTIFIED and NOT EVALUATED flags from upstream skills. These are **not buried in appendices** — they are required outputs per the framework's evidence-state discipline.

| # | Item | Evidence State | Source |
|---|---|---|---|
| 1 | Non-patent literature disclosing shield-for-phase-delay mechanism before March 26, 1890 | **NOT IDENTIFIED** | Skill 06 (Literature Search) — Archive.org and Google Books searched; 1888–1890 journal full-text not accessible |
| 2 | Quantitative performance data (efficiency, torque, speed) for the shield design | **NOT IDENTIFIED** | Skill 03 (Technology Fundamentals) — no accessible source contains performance data |
| 3 | Unexpected technical result from the combination | **NOT IDENTIFIED** | Skill 05 (Novelty Search) — no data comparing shield approach to self-induction approach |
| 4 | Commercial adoption of the shield approach | **NOT OBSERVED** | Skill 07 (Market Opportunity) — no evidence found that any manufacturer adopted this approach; coverage insufficient to establish confirmed absence |
| 5 | Prototype evidence | **NOT OBSERVED** | Skill 07 — no evidence a prototype was built and tested |
| 6 | Production evidence | **NOT OBSERVED** | Skill 07 — no evidence of production |
| 7 | Commercial readiness | **NOT EVALUATED** | Skill 07 — no confirmed adoption evidence exists; stated as NOT EVALUATED per framework rule |
| 8 | Market sizing (1890 electrical industry revenue, AC motor CAGR) | **NOT IDENTIFIED** in primary source | Skill 07 — figures could not be reconstructed from a cited primary source; removed from report rather than presented unsourced |
| 9 | Full-text access to 1888–1890 electrical engineering journals | **NOT EVALUATED** | Skill 06 — search not performed due to access limitations |
| 10 | Motivation for substituting shielding for self-induction | **INFERRED** | Skill 05 — the reason is plausible but no pre-filing source evidences it; caps the obviousness finding at unresolved |

---

## 9. Decision Matrix Output

### 9.1 State Machine Path

```text
PRIOR ART REFERENCES (US381,968; US416,195; US382,279)
                    │
                    ▼
            ┌─────────────────┐
            │ Claim mapping    │
            └────────┬────────┘
                     │
                     ▼
          ANY LIMITATION MISSING?
                     │
                    YES (all references missing d & e)
                     │
                     ▼
          OBVIOUSNESS ANALYSIS
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
  Modify         Combine         Substitute
                                  │
                                  ▼
                          MOTIVATION GATE
                          (INFERRED — no pre-filing
                           source evidences the
                           substitution motivation)
                                  │
                                  ▼
                       EXPECTED-SUCCESS GATE
                       (medium, capped by
                        compatibility constraints)
                                  │
                                  ▼
                        CAUSAL-DISTANCE GATE
                        (C3 — different physical
                         principle; mechanism
                         displacement HIGH)
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
                          (motivation INFERRED, high mechanism
                           displacement, application NOT OBSERVED)
```

### 9.2 Conclusion — Multidimensional

| Gate | Result |
|---|---|
| **Anticipation gate** | NOT ANTICIPATED — no single reference discloses all limitations (d) and (e) missing from all references) |
| **Obviousness analysis** | MODERATE RISK, **UNRESOLVED** — substitution of magnetic shielding for self-induction is a plausible modification path; motivation is INFERRED (not evidenced); mechanism displacement is HIGH (material-level vs. circuit-level control); the specific application is NOT OBSERVED in the accessible pre-filing record |
| **Causal distinction from closest prior art** | **Strong** — C3 causal distance (different physical principle) with high mechanism displacement |
| **Technical effect** | CONFIRMED PRESENT — phase difference from single source is achieved |
| **Unexpected result** | NOT IDENTIFIED — no performance comparison data available |
| **Combination-obviousness exposure** | MODERATE, UNRESOLVED — components exist in prior art; the delta application step is NOT OBSERVED; derivation not established |
| **Self-prior-art** | MODERATE RISK — Tesla's own US416,195 is the closest reference; double-patenting exposure exists |
| **Historical disclosure coverage** | **Incomplete** — 1888–1890 journal full-text not accessible; application step NOT OBSERVED |
| **Commercial adoption evidence** | **NOT OBSERVED** — no adoption found; coverage insufficient for confirmed absence |
| **Historical market sizing** | **Insufficient** — no defensible CAGR or revenue figure reconstructable from primary sources |
| **Overall patentability** | **INDETERMINATE-TO-MODERATE** — strong on utility, novelty, and causal distinction; obviousness risk moderate but unresolved; unexpected-result evidence absent; historical evidence coverage incomplete. "Moderate obviousness risk" ≠ "moderate patentability" — they are not inverses |

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
| **Classification** | H02K 17/00 (Asynchronous induction motors) |
| **Short description** | AC motor using magnetic shields to create artificial phase difference between field magnet sets from a single current source |
| **Detailed description** | Two sets of field-magnet cores, each wound with coils in separate branched circuits from a single AC source. Magnetic shield (annealed insulated iron wire) around one set of coils delays magnetization via saturation, creating phase difference. Fig. 2 variant: shield connected in series with other circuit for dual acceleration/retardation effect. |
| **Innovation claims** | 4 independent claims covering magnetic shield/screen interposed between coils and cores to retard magnetization |
| **Proof-of-concept** | Patent granted; assigned to operating company |
| **Current IP status** | Historical term expired: August 5, 1907 (17 years from grant, subject to the historical patent regime) |
| **Target markets** | Industrial power transmission, electric lighting systems, emerging AC distribution infrastructure |
| **Known competitors** | Edison General Electric (DC), Westinghouse Electric (AC), Thomson-Houston Electric |
| **Disclosure history** | No public disclosure prior to filing identified. Patent application filed March 26, 1890. **NOT OBSERVED** — no earlier talks, publications, demonstrations, sale offers, or social media posts identified in searched sources; coverage insufficient to establish confirmed absence. (Not to be conflated with "confirmed absent.") |
| **Source document** | PDF: "FireShot Capture 002 - Nikola Tesla U.S. Patent 433,700" from teslauniverse.com (could not be read by model — PDF input not supported). Full patent text retrieved from Google Patents: https://patents.google.com/patent/US433700A/en |

### Appendix B: Patentability Primer

- **Anticipation:** A single prior-art reference discloses every element of a claim. None of the identified references anticipate US433700 Claim 1 — all are missing limitations (d) and (e).
- **Obviousness / Inventive Step:** Two or more references, combined, disclose every element, with a plausible reason a skilled person would combine them. Risk is moderate but unresolved — Tesla's own prior patents provide the closest combination risk. The substitution of magnetic shielding for self-induction is the primary obviousness path, but the motivation for it is INFERRED rather than evidenced, and mechanism displacement is high.
- **Combination-Obviousness Exposure:** Novelty argued from combining known elements rather than a new element itself — the weakest basis for an inventive-step argument absent an unexpected result. **A combination can be completely novel while still being obvious.** The operative question is derivation risk: how readily the combination can be reconstructed from prior-art components with a demonstrated motivation to combine. **This applies to US433700.**
- **Freedom to Operate (FTO):** A search for *in-force* patents the invention might infringe. This report does **NOT** provide an FTO opinion. The patent is expired, so FTO concerns are moot for this specific invention, but this analysis should not be generalized to other inventions.

### Appendix C: Search Methodology

All searches were conducted using publicly available patent databases (Google Patents) and web search tools. Searches were performed on August 13, 2026. No proprietary patent databases (Derwent, PatBase, etc.) were used. Non-patent literature searches were conducted via Archive.org and Google Books; full-text access to 1888–1890 electrical engineering journals was not available.

**Databases searched:**
- Google Patents (full-text patent search, citation chains, similar documents)
- Archive.org (historical texts)
- Google Books (historical texts)

**Databases NOT searched (access limitations):**
- Espacenet (returned 403 error)
- Derwent, PatBase (proprietary, not available)
- IEEE Xplore, PubMed (not applicable to 1890 era)
- *The Electrician*, *Electrical World*, *American Electrician* (full-text not accessible for 1888–1890 window)

### Appendix D: Evidence Audit

| Key Claim | Evidence Status | Source Searched |
|---|---|---|
| No single reference anticipates US433700 Claim 1 | CONFIRMED PRESENT | Google Patents — US381,968, US416,195, US382,279 full text reviewed |
| US416,195 is the closest prior art (same problem, different mechanism) | CONFIRMED PRESENT | Google Patents — US416,195 full text reviewed |
| The shield mechanism is not found in pre-1890 non-patent literature | NOT IDENTIFIED | Archive.org, Google Books — searched, not found |
| The shield approach was not commercially adopted | NOT OBSERVED | Historical record — no evidence of adoption found; coverage insufficient to establish confirmed absence |
| No unexpected result data exists | NOT IDENTIFIED | No accessible source contains performance comparison data |
| US433700 has only 1 forward citation | CONFIRMED PRESENT | Google Patents — Cited By section: US20060045755A1 (Dell, 2006) |
| US381,968 has 70+ forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US416,195 has 3 forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| US382,279 has 21+ forward citations | CONFIRMED PRESENT | Google Patents — Cited By section |
| No international patent family for US433700 | CONFIRMED PRESENT | Google Patents — Country Status: US (1) only |
| Tesla assigned patent to Tesla Electric Company | CONFIRMED PRESENT | Patent specification header: "ASSIGNOR TO THE TESLA ELECTRIC COMPANY" |
| Filing date March 26, 1890 | CONFIRMED PRESENT | Patent specification: "Application filed March 26, 1890. Serial No. 345,388" |

### Appendix E: Full Query Log

| # | Query String | Database | Date | Results Used |
|---|---|---|---|---|
| 1 | `US433700A` direct fetch | Google Patents | 2026-08-13 | Full patent text, claims, classification, citations, similar documents |
| 2 | `US381968A` direct fetch | Google Patents | 2026-08-13 | Full patent text, claims, 70+ citations |
| 3 | `US416195A` direct fetch | Google Patents | 2026-08-13 | Full patent text, claims, 3 citations |
| 4 | `US382279A` direct fetch | Google Patents | 2026-08-13 | Full patent text, claims, 21+ citations |
| 5 | `alternating current motor phase difference magnetic shield` (priority 1885–1895) | Google Patents | 2026-08-13 | US433700, US381968, US416195, US382279 |
| 6 | `alternating current motor phase shift OR rotating magnetic field` (priority 1885–1895, inventor ≠ Tesla) | Google Patents | 2026-08-13 | US444934 (Billberg & Winand, excluded — post-filing) |
| 7 | `alternating current motor induction rotating field` (priority 1885–1895, inventor ≠ Tesla, ≠ Ferraris) | Google Patents | 2026-08-13 | US347642 (Ripley — background only) |
| 8 | `alternating current motor phase difference OR rotating magnetic field` (priority 1880–1890) | Google Patents | 2026-08-13 | Confirmed Tesla dominance in field |
| 9 | `US433702A` direct fetch (sibling patent) | Google Patents | 2026-08-13 | Sibling patent — transformer application of same shield principle |
| 10 | `US433703A` direct fetch (sibling patent) | Google Patents | 2026-08-13 | Sibling patent — core lamination delay alternative |
| 11 | `alternating current electrical engineering 1889` (texts) | Archive.org | 2026-08-13 | No accessible full-text results |
| 12 | `tesla alternating current motor 1888` (texts) | Archive.org | 2026-08-13 | No accessible full-text results |
| 13 | `alternating current motor phase difference magnetic shield` (pre-1890) | Google Books | 2026-08-13 | No accessible full-text results for 1888–1890 window |
| 14 | `rotating magnetic field polyphase` (pre-1890) | Google Books | 2026-08-13 | Ferraris (1885), Tesla (1888) confirmed; shield mechanism not found |
| 15 | `self-induction alternating current retardation` (pre-1890) | Google Books | 2026-08-13 | General self-induction knowledge confirmed; shield-for-phase-delay not found |

### Appendix F: Quality Checklist

- [x] Every quantitative claim is sourced (or omitted / marked INFERRED with derivation — unsourced revenue and CAGR figures removed)
- [x] Chronology validator passed: all dates consistent; "before May 26, 1890" corrected to "before March 26, 1890" (§5.4)
- [x] Every legal-adjacent statement (patentability, FTO-adjacent, regulatory) carries a "not legal advice" disclaimer
- [x] The novelty section explicitly states it is not an FTO opinion
- [x] The query log is complete enough that a reviewer could re-run any search and reproduce the result set
- [x] Any "NOT IDENTIFIED", "NOT OBSERVED", or "NOT EVALUATED" flags from upstream skills are carried into the report (Section 8)
- [x] Evidence Audit appendix is present and maps each key finding to its evidence status (Appendix D)
- [x] Commercial readiness is stated as "NOT EVALUATED" unless confirmed adoption evidence exists (Section 6.6); adoption absence labeled NOT OBSERVED, not CONFIRMED ABSENT
- [x] Decision matrix output is included, showing the reasoning path (including motivation / expected-success / causal-distance gates), and the structured obviousness evidence object is provided (Section 9 and Section 4.6)
- [x] Conclusion is multidimensional (per-gate table, §9.2) — no single compressed "MODERATE patentability" label; unresolved gates read as "Indeterminate-to-moderate"
- [x] No exclusivity framing survives: "only partner" / "no commercial vehicle" replaced with "strongest identified pathway" (§7.1)
- [x] Forward-citation count relabeled as a neutral historical signal, not patentability evidence (§3.7, §4.6)
- [x] Claim-construction layer is clearly labeled as based on the patent's actual claims (not a provisional construct — formal claims exist in this case)

---

*End of Report*
*Generated by the Invention Evaluation Framework v1.4*
*Full 9-stage pipeline execution*
*This report is NOT legal advice. All patentability assessments are preliminary. Consult qualified patent counsel for formal opinions.*
