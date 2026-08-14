# Design Spec — Invention Evaluation Framework v1.5

**Date:** 2026-08-14
**Status:** Approved (brainstorming complete; all 10 proposals locked)
**Supersedes:** v1.4 (2026-08-13)

## Goal

Upgrade the Invention Evaluation Framework from v1.4 to v1.5 by implementing ten proposals from the post-run critique of the US433,700 end-to-end evaluation. The core architectural principle of v1.5: **the framework's native output is a set of deliberately non-collapsible analytical dimensions, not a scalar patentability score.**

## The ten proposals and their locked decisions

### 1. Mechanism Distance (C0–C4) — renamed from "causal distance"

The existing C0–C4 scale is retained and renamed **Mechanism Distance**. Answers: *How far does the claimed physical causal mechanism move from the reference mechanism?*

| Level | Meaning |
|---|---|
| C0 | Mechanistically identical |
| C1 | Essentially the same mechanism with a minor physical variation |
| C2 | Same underlying physical principle, different intervention point/configuration |
| C3 | Different physical mechanism producing substantially the same effect |
| C4 | Fundamentally different causal mechanism / no meaningful causal machinery shared |

### 2. Design-Choice Distance (D0–D4) — new orthogonal scale

Answers: *How much conceptual/design selection is required to get from what was known to what was claimed?* Defined around the **decision required**, not around novelty.

| Level | Definition |
|---|---|
| D0 | Direct/default choice — natural or routine implementation of the known teaching |
| D1 | Routine alternative — one of a small number of directly suggested alternatives |
| D2 | Non-default selection — choosing among several viable alternatives with ordinary trade-offs; path visible in prior art |
| D3 | Cross-domain/application leap — recognizing a known principle/component can perform a different function, or transferring known machinery to a materially different intervention point, without direct teaching of that move. **D3 is a diagnostic, not an obviousness verdict.** |
| D4 | Unsignposted inventive bridge — requires a new insight, substantial engineering development, or a design move with no credible path or expectation of success in the accessible design space |

**Rules:**
- C and D are **mandatory, reference-relative, orthogonal** fields in every obviousness evidence object.
- **Never mathematically combined** (no C2+D3=5, no weighted average, no product). Reported as `C2 / D3` with each dimension explained independently.
- D is assigned **per reference pathway**, never globally: `reference: US424036 → C2 / D3`, `reference: US416195 → C3 / D3`.

### 3. Search Coverage (negative-evidence metadata)

**Coverage is mandatory on** `NOT OBSERVED`, `NOT IDENTIFIED`, and `CONFIRMED ABSENT`. Not required on `CONFIRMED PRESENT` (positive claims are anchored by their citation).

```yaml
evidence_state:
  status: NOT OBSERVED
  coverage:
    scope: "..."
    temporal_scope: "..."
    source_domains: [...]
    search_depth: "partial"
    completeness: "LOW"
    limitations: [...]
```

**Coverage level:** LOW / MEDIUM / HIGH / EXHAUSTIVE (LOW = narrow/partial, absence inference weak; MEDIUM = multiple relevant sources with gaps; HIGH = broad targeted search with documented residual gaps; EXHAUSTIVE = demonstrably bounded and substantially complete domain).

**Negative Evidence Coverage Rule (locked):** Coverage is metadata about the evidentiary search, not evidence itself. Coverage may qualify the reliability of a negative finding and may authorize a targeted re-evaluation, but it MUST NOT automatically change the evidence state. `CONFIRMED ABSENT` additionally requires a defined and sufficiently complete evidence universe.

**Distinct negative-state semantics:**
- `NOT OBSERVED` = negative search result (universe incomplete / coverage insufficient)
- `NOT IDENTIFIED` = negative identification result (documentary search target)
- `CONFIRMED ABSENT` = bounded negative finding (requires coverage + bounded universe: type, definition, completeness, exclusions)

**Prohibited:** automatic `HIGH coverage → CONFIRMED ABSENT`; `LOW coverage + CONFIRMED ABSENT` at all.

**Epistemic rule:** *You can increase search coverage without increasing certainty. You need new evidence to increase certainty.*

### 4. Motivation as a first-class evidence object

One motivation object per obviousness evidence object (path-independent). `proposed_modification_paths` carry `motivation_delta` only when a path materially differs.

```yaml
motivation:
  proposition: "..."
  direct:      [{source, support}]
  analogous:   [{source, support}]
  inferred:    [{source, support}]
  contradicted:[{source, support}]
  status: GROUNDED | PARTIALLY_GROUNDED | INFERRED | RECONCILIATION_REQUIRED
```

**Deterministic derivation:**

| Evidence condition | Status |
|---|---|
| ≥1 direct, no unresolved contradiction | GROUNDED |
| No direct, ≥1 analogous, no unresolved contradiction | PARTIALLY GROUNDED |
| Only inferred | INFERRED |
| Any contradicted evidence | RECONCILIATION REQUIRED |

**Guardrails:** a higher category never erases contradiction (direct + serious contradictory → RECONCILIATION REQUIRED); multiple analogous sources never accumulate into direct evidence.

**Key distinction:** Motivation asks whether the skilled person had *reason* to make the move; the modification path asks *what move* they would make. A plausible path is not evidence of motivation.

### 5. Knowledge decomposition (known component ≠ known function ≠ known combination ≠ known application)

Evidence-stated flags (not bare booleans), each carrying an evidence state + source:

```yaml
component_known: CONFIRMED PRESENT (source)
principle_known: CONFIRMED PRESENT (source)
function_known: CONFIRMED PRESENT (source)
combination_known: NOT OBSERVED (coverage)
application_known: NOT OBSERVED (coverage)
motivation_to_combine: INFERRED
```

Lives in the Causal Bridge Test as its `prior_state`; the obviousness evidence object references it (defined once, no duplication).

### 6. Remove the overall patentability score from the default output

- The native output is the **per-gate table** (novelty / obviousness risk / unexpected result / historical coverage / commercial viability), each with status + confidence.
- An executive score is **derived only on request**, marked as a derived executive summary (never a pipeline output). "Indeterminate-to-[level]" survives only as the derivation rule for that optional score.
- Quality checklist gains: "No scalar patentability label appears in the default conclusion output."

### 7. Causal Bridge Test — the top-level construct

The novelty search skill's obviousness section is reorganized around the Causal Bridge Test as the mandatory centerpiece; the obviousness evidence object (with C/D distances, motivation object, coverage, modification paths) becomes its audit trail.

```yaml
causal_bridge_test:
  prior_state:
    known_objective: true
    known_components: true        # ← knowledge decomposition (proposal 5)
    known_principles: true
  claimed_state:
    claimed_configuration: true
    claimed_effect: true
  bridge:
    required_change: [...]
  bridge_evidence:
    direct_pre_filing: false
    analogous_pre_filing: true
    inventor_self_art: true
    general_science: true
    post_filing: excluded
  motivation: {...}               # ← first-class object (proposal 4)
  expectation_of_success:
    technical: medium
  unexpected_result:
    identified: false
  bridge_status: TRAVERSED | UNTRAVERSED | UNRESOLVED
```

**bridge_status semantics:**
- **TRAVERSED** — evidence shows a skilled person would cross the bridge (obviousness strengthens)
- **UNTRAVERSED** — evidence shows the bridge was not reasonably crossable (e.g., unexpected result, technical failure, high design-choice distance with no path) — non-obviousness argument
- **UNRESOLVED** — neither direction is evidenced (the default when motivation is INFERRED or application is NOT OBSERVED)

**Central question:** *What exactly has to be invented between the prior art and the claim?*

### 8. Architecture summary — the non-collapsible dimensions

| Dimension | Construct | Question it answers |
|---|---|---|
| Mechanism Distance | C0–C4 | How different is the physical machinery? |
| Design-Choice Distance | D0–D4 | How much conceptual/design selection is required? |
| Coverage | LOW/MEDIUM/HIGH/EXHAUSTIVE | How extensively was the negative proposition searched? |
| Motivation | GROUNDED/PARTIALLY GROUNDED/INFERRED/RECONCILIATION REQUIRED | Is there evidence a skilled person would make the move? |
| Modification Path | proposed_modification_paths | What specific change is proposed? |
| Bridge Status | TRAVERSED/UNTRAVERSED/UNRESOLVED | Was the causal bridge crossable on the evidence? |

These facts coexist without forcing a single scalar judgment. Example output for US433,700: *C2/D3 against US424,036; C3/D3 against US416,195; Motivation: PARTIALLY GROUNDED; Negative search coverage: HIGH.*

## Files to change

1. `GLOSSARY.md` — rename causal distance → mechanism distance; add D0–D4, coverage schema + Negative Evidence Coverage Rule, motivation object + derivation table, knowledge decomposition, Causal Bridge Test + bridge_status, remove overall score from Multidimensional Decision Output
2. `skill-05-conduct-novelty-search/SKILL.md` — reorganize obviousness section around the Causal Bridge Test; add D-distance, coverage, motivation object, knowledge decomposition, bridge_status
3. `skill-09-compile-report/SKILL.md` — remove overall score from default conclusion; add executive-score derivation rule; update quality checklist
4. `skill-07-analyze-market-opportunity/SKILL.md` — coverage schema for NOT OBSERVED adoption claims
5. `skill-06-conduct-literature-search/SKILL.md` — coverage for NOT IDENTIFIED findings
6. `skill-04-conduct-patent-landscape/SKILL.md` — coverage for negative landscape findings
7. `DIGEST.md` — update non-negotiables
8. `INDEX.md` — update
9. `PIPELINE_STATE.md` — v1.5 change log
10. New: `docs/superpowers/specs/2026-08-14-invention-evaluation-framework-v15-design.md` (this file)

## Validation

Re-run the Tesla US433,700 evaluation under v1.5 (new report file `report-tesla-us433700-e2e-v15.md`) to exercise every new construct end-to-end: C/D distances per reference pathway, coverage objects on all negative findings, the motivation object (expect PARTIALLY GROUNDED or INFERRED), the knowledge decomposition, the Causal Bridge Test (expect bridge_status UNRESOLVED), and the per-gate-only default conclusion.