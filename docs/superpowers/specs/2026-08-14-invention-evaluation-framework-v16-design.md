# Design Spec — Invention Evaluation Framework v1.6

**Date:** 2026-08-14
**Status:** Approved (brainstorming complete; architecture locked section-by-section)
**Supersedes:** v1.5 (2026-08-14)
**Versioning:** Breaking change. The v1.5 evidence ontology is removed from the active framework; v1.5 reports remain as historical artifacts.

## Goal

Upgrade the Invention Evaluation Framework from v1.5 to v1.6 by replacing the epistemic foundation. v1.5 treated uncertainty as an acceptable output state (`NOT FOUND`, `NOT OBSERVED`, `INFERRED`, `UNRESOLVED`, `MEDIUM completeness`). v1.6 makes those states structurally impossible as terminal conclusions.

**Governing principle (top of DIGEST, GLOSSARY, Skills 01/05/06/07/09):**

> **Unsupported assertions are errors. Missing evidence is a work queue, not an answer.**

**Core rule:**

> **A proposition is either admitted as an evidence-backed finding or it remains in the work queue. There is no third category where the model is allowed to sound knowledgeable without having established the proposition.**

**The evaluator is not permitted to convert the absence of successful research into a fact about reality.** It either establishes the proposition, or continues the work, or documents that the proposition remains unestablished after the prescribed workflow.

## The failure mode being eliminated (US7216695 phenotype)

The v1.5 engine produced rows like:

- `Various SBIR awards for spray cooling in military applications` → `Confirms market relevance` — no award numbers, agencies, recipients, dates, titles, amounts, URLs, or relationship to the patented technology. An unsupported inference masquerading as a finding.
- `Research on spray cooling for UAVs and military applications` — a research task description, not a finding. No paper identity, no demonstrated result.
- `NAICS 334419 – INFERRED` — a guessed classification.
- `completeness: MEDIUM` — "I did some searching" as a terminal state.

v1.6 makes these rows **structurally impossible**: a finding row does not exist unless its evidence schema fully validates.

## Locked architecture — three layers

```
┌─────────────────────────────────────────────┐
│ EVIDENCE LAYER                              │
│                                             │
│ CONFIRMED PRESENT                           │
│ CONFIRMED ABSENT                            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ WORK LAYER                                  │
│                                             │
│ NOT_STARTED          (engine-internal)      │
│ SEARCHING                                   │
│ ESCALATING                                  │
│ REQUIRES VERIFICATION                       │
│ BLOCKED             ← avenue-level          │
│ EXHAUSTED           ← proposition-level     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ ANALYTICAL LAYER                            │
│                                             │
│ evidence → inference → conclusion           │
│                                             │
│ inference is NEVER evidence                 │
└─────────────────────────────────────────────┘
```

**Governing invariant:** Work-state transitions cannot create evidence. Evidence can only be created by verified source support.

**Hard anti-collapse invariants:**

- `EXHAUSTED ≠ CONFIRMED ABSENT`
- `BLOCKED ≠ CONFIRMED ABSENT`
- `REQUIRES VERIFICATION ≠ CONFIRMED PRESENT`
- `INFERENCE ≠ EVIDENCE`
- **Search completion is not evidence.**

## Section 1 — Epistemic architecture

### Evidence layer (what the admissible record establishes about the proposition)

- **CONFIRMED PRESENT** — directly verified in an admissible source with exact source identity, location/citation, and proposition-level support.
- **CONFIRMED ABSENT** — specifically tested and absent within a defined, bounded evidence universe whose sufficiency requirements have been satisfied. The finding object must carry `absence_basis` (bounded_universe_definition, sufficiency_test) — the bounded universe is inseparable from the finding.

### Work layer

- **NOT_STARTED** — workflow initialization state, engine-internal, never exposed in reports. Distinguishes "search hasn't begun" from "search underway."
- **SEARCHING** — initial search in progress.
- **ESCALATING** — current channel exhausted; moving to the next required avenue.
- **REQUIRES VERIFICATION** — evidence or a source has been located, but its authenticity, provenance, completeness, interpretation, or conflict status has not yet been resolved. Flow: SOURCE LOCATED → REQUIRES VERIFICATION → validated → PRESENT / contradicted → reconcile conflict / unusable → escalate or exclude.
- **BLOCKED** — avenue-level disposition: the specified avenue cannot be executed, and the reasonable alternate access routes defined for that avenue have been attempted and failed. Other avenues may remain available.
- **EXHAUSTED** — proposition-level termination state: all required avenues have been executed, logged, and dispositioned, and evidence is still insufficient. **Never evidence. Never authorizes a factual conclusion.**

### Analytical layer

Evidence → inference → conclusion. Inference is a labeled analytical step, never an evidence state. The v1.5 Evidence → Inference → Conclusion firewall persists.

### Old-state mapping

| v1.5 | v1.6 disposition |
|---|---|
| CONFIRMED PRESENT | Evidence state |
| CONFIRMED ABSENT | Evidence state, bounded + sufficient |
| NOT OBSERVED | Avenue/search metadata |
| NOT IDENTIFIED | Avenue/search metadata |
| INFERRED | Analytical inference |
| NOT EVALUATED | Work state (NOT_STARTED → SEARCHING) |
| CONTESTED | Verification/reconciliation work state |

### Excluded-from-report rule (brutally explicit)

An unsupported proposition does not become a negative finding merely because the search protocol ended. It is **omitted from the factual findings** and retained only in the operational audit as an unestablished proposition. The engine cannot transform `proposition: "The invention was commercially adopted." / work_state: EXHAUSTED` into "No commercial adoption was identified" — that sentence is itself a factual negative claim. The only allowable output is "Commercial adoption could not be established from the completed evidence protocol," confined to the Evidence Limitations / Unestablished Propositions section.

## Section 2 — Evidence Sufficiency Gate

The gate is the **only path** by which a proposition becomes a finding. Runs per proposition, per skill:

```text
PROPOSITION
   ↓
1. Required evidence type identified (schema selected)
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
   └── NO  → SEARCH ESCALATION (Section 3)
```

Steps 4 and 6 together form the **proposition-identity firewall**: the source must support the exact proposition, and the proposition must be scoped correctly. "Spray cooling was used in military electronics" does not establish "US7216695 Claim 1 was commercially deployed."

### Schema-driven required standard

Every proposition type has a defined minimum evidence schema. **A finding row does not exist unless every required schema field is populated with an exact identifier.** This is the most important implementation rule in v1.6 — it makes the malformed answer structurally impossible rather than merely discouraged.

| Proposition type | Skills | Required schema fields (exact identifiers) |
|---|---|---|
| Prior-art disclosure | 04, 05 | patent/publication ID, jurisdiction, date, relevant passage, claim-element mapping |
| Non-patent literature disclosure | 06 | authors, title, venue, date, DOI/report no., URL, experimental system, technology, application, demonstrated result, relevance |
| Market relevance / demand | 07 | award/procurement schema: agency, solicitation/award ID, recipient, date, amount (if available), title, URL, relevant passage — or industry-report schema |
| Market sizing | 07 | defined market boundary, geography, time period, figure, source, reconciliation, derivation |
| NAICS classification | 07 | official taxonomy source, exact code, official title, edition year, basis (definition match / activity match) |
| Commercial adoption | 07 | product-identity link (commercial product identifiable as embodying the claimed technology), source, date |
| Regulatory regime | 03 | governing statute/regulation, why technology falls inside/outside it |
| Partner fit | 08 | what they sell, what they buy, technical need, mapping to invention |
| Motivation | 05 | first-class object (v1.5, retained) |
| Knowledge-decomposition flags | 05 | evidence-stated flags (v1.5, retained) |

### Corroboration (schema-driven, not universal)

```yaml
corroboration:
  required: true
  minimum_independent_sources: 2
  source_independence_rule: MATERIAL_PROVENANCE_INDEPENDENCE
```

- **Independent source** = materially independent provenance. Republished, syndicated, scraped, mirrored, press-release-derived, or citation-chain-dependent copies of the same underlying evidence count as one source. An SBIR.gov record + company press release quoting it + news article quoting the press release = **one evidence lineage**.
- `minimum_independent_sources` is per-schema: patent grant date may need 1 primary record; commercial adoption needs 2 independent product-identity links; historical absence needs a bounded universe + 2 independent records.
- Single-source support yields at most `CONFIRMED PRESENT` with a single-source caveat — never `CONFIRMED ABSENT`.

### Contradiction handling

Contradictory evidence → `REQUIRES VERIFICATION` → reconcile; if irreconcilable, the proposition is **excluded** (unestablished), never reported as contested.

### Atomic admission

Proposition admission is all-or-nothing. If one mandatory field is missing, the proposition fails sufficiency. "Mostly supported" is not a state.

## Section 3 — Search Escalation Protocol

### Avenue vs. proposition states

- `BLOCKED` is an **avenue disposition** (one avenue inaccessible; alternatives still climbable).
- `EXHAUSTED` is a **proposition-level termination state** (all required avenues dispositioned).
- A blocked avenue does not imply the proposition is excluded; other avenues can still complete.

### Per-skill avenue checklists

Each search skill defines its mandatory avenues with **deterministic priority ordering** (same proposition + same skill + same avenue configuration → same escalation ladder; the model cannot skip avenues mid-run).

**Default avenue template** (per search skill, customized per skill's proposition types):

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

Each avenue carries its audit record:

```yaml
search_escalation:
  avenues:
    - id: A1
      name: primary_source_search
      priority: 1
      required: true
      status: COMPLETE | BLOCKED | NOT_APPLICABLE | REQUIRES_VERIFICATION
      record:
        searches_run: []
        sources_consulted: []
        relevant_results: []
        exclusions: []
        limitations: []
        completion_basis: ""
```

Avenue status semantics:

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

1. `EXHAUSTED` may be emitted only when every required avenue has a completed audit record or a rule-justified `BLOCKED`/`NOT_APPLICABLE` disposition.
2. `EXHAUSTED` never constitutes evidence and never authorizes a factual conclusion.
3. Supplemental avenues are allowed only as explicit logged exceptions — never part of termination logic.
4. Search completion is not evidence (`EXHAUSTED ≠ CONFIRMED ABSENT`).

### Post-EXHAUSTED disposition

The proposition is omitted from factual findings and retained only in the operational audit as an unestablished proposition, with `barrier_type` and `remaining_evidentiary_barrier`.

## Section 4 — Finding Object & Proposition Identity

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
      award_id: ""                  # exact identifier — mandatory
      recipient: ""
      award_date: ""
      award_amount: ""
      relevant_passage: ""
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

### Rules

- **Row non-existence:** if any mandatory schema field is empty, the finding object does not exist — there is nothing to report.
- **Proposition identity:** each proposition carries a stable `proposition_id` + `proposition_version`. The same ID carries the same evidence state across skill hand-offs — no drift, no silent upgrade. **A proposition ID may not change evidence schema, scope, or proposition text without a version increment** (P-07-003 v1 → P-07-003-v2 or a new ID). This prevents silent narrowing ("Was the invention adopted?" → "Was the invention mentioned in a commercial source?").
- **Source identity:** durable `source_identity` fields beyond URL — the SBIR object is defensible even if the URL later changes.
- **Scope fields are schema-specific:** `proposition_scope.required_fields` is declared by the schema; a jurisdiction-neutral literature proposition is not forced to invent a jurisdiction.
- **Atomic admission:** the gate is all-or-nothing per proposition.

## Section 5 — Report Architecture (skill-09)

The report has three conceptual areas. **Operational Audit cannot flow backward into Established Findings** — a completed search does not become a fact.

### 1. Established Findings

Only rows that passed the Sufficiency Gate (`CONFIRMED PRESENT` / `CONFIRMED ABSENT`), each rendered from its finding object with full provenance.

### 2. Analytical Conclusions

Per-gate results whose premises are established findings. Every analytical conclusion carries a **premise map**:

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

Hard trace: Conclusion → Premises → Finding objects → Sources. **No orphan conclusions.** No conclusion may use a premise whose status is a work state (e.g., `EXHAUSTED`) as though it were evidence.

**UNRESOLVED may not appear as a terminal analytical conclusion at all.** Three outcomes only:
- More work needed → work layer
- All work exhausted → exclude proposition
- Supported evidence → analytical conclusion permitted

### 3. Operational Audit

Unestablished propositions and search records:

- Each excluded proposition: `proposition_id`, work state, avenue dispositions (`COMPLETE`/`BLOCKED`/`NOT_APPLICABLE` + rule_id), and:
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
- The reproducible query log = the full escalation ladder (all avenue records, in priority order).
- **Allowed language:** "Commercial adoption could not be established from the completed evidence protocol."
- **Prohibited language** (and semantic equivalents): "Not found," "No commercial adoption was identified," "No evidence of adoption exists," "appears absent," "there is no evidence that…," "apparently none," "likely not," "could not locate," "no known," "none identified," "no record was found," "Inferred," "Medium completeness" — unless explicitly confined to the Operational Audit describing search activity rather than making a factual claim.

### Executive summary

Derived only on request, labeled as derived, and formally constrained:

```text
Executive Summary ⊆ Established Findings + Analytical Conclusions
```

The audit may be referenced ("Several evidentiary gaps remain and are documented in the Operational Audit") but never converted into factual prose.

## Section 6 — File-by-File Change Map

### Propagation chain (mandatory parity)

```text
ROOT SOURCE OF TRUTH
        ↓
invention-evaluation-engine/
        ↓
install.sh
        ↓
~/.opencode/skills/
```

**The package and installed copy are generated/propagated artifacts, never independent sources of truth.** Root/package/install parity is mandatory: the verifier compares a canonical digest or normalized content hash for all active framework files across the three layers.

### Docs (root + `invention-evaluation-engine/docs/`, mirrored)

| File | v1.6 changes |
|---|---|
| `DIGEST.md` | Governing principle at top. Replace item 12 (evidence-state discipline) with the three-layer hierarchy + anti-collapse invariants. Replace item 13 (Negative Evidence Coverage Rule) with **Evidence Sufficiency & Search Escalation Rule**. Replace item 16 ("insufficient evidence is a valid output") with: missing evidence is a work queue. Rewrite items 9/17/23 that use INFERRED/UNRESOLVED as terminal states. Add atomic-admission and proposition-identity rules. |
| `GLOSSARY.md` | Replace the 7-state ontology with the three layers. Add: work states, Sufficiency Gate sequence, avenue protocol (checklist, `avenue_record`, statuses, priority, `rule_id`), finding object + `source_identity` + `absence_basis`, per-proposition-type schema table, corroboration rules, `barrier_type` enum, prohibited-language list. Update dependent constructs: obviousness evidence object, motivation object, Causal Bridge Test (`bridge_status` UNRESOLVED → work state), decision matrix, multidimensional output. |
| `INDEX.md` | Dependency graph + entry points updated for the new vocabulary. |
| `PIPELINE_STATE.md` | v1.6 change log (breaking change from v1.5). |
| `README.md` | v1.6 description. |

### Skills (root + package, mirrored)

| Skill | v1.6 changes |
|---|---|
| 01 overview | Pipeline description, state vocabulary, evidence-grade preservation → **proposition-identity preservation** (IDs + versions across hand-offs). |
| 02 submission | Minimal — disclosure/sale-offer capture unchanged. |
| 03 technology fundamentals | Regulatory regime schema (governing statute, inside/outside basis); IPC/CPC candidates must be exact from official sources; performance-data propositions get schemas. |
| 04 patent landscape | Negative landscape findings → avenue records; filing-volume/assignee propositions get schemas. |
| 05 novelty search | **Largest change.** Prior-art disclosure schema; Sufficiency Gate for anticipation/obviousness propositions; avenue checklist; obviousness object + motivation object + bridge test updated (no INFERRED/UNRESOLVED terminal states). |
| 06 literature search | Paper schema (authors/title/venue/date/DOI/system/result/relevance); avenue records. |
| 07 market opportunity | NAICS exact schema; market-sizing schema; adoption product-identity link; SBIR/procurement award schema; avenue checklist. |
| 08 partners | Partner-fit schema (sell/buy/need/mapping); avenue checklist. |
| 09 compile report | Three-area architecture; premise maps; Executive Summary constraint; prohibited language; Operational Audit. |

### Verification machinery

`verify.sh` gains:

1. **Legacy-terminology semantic scan** — detect legacy states used as active semantics, not just strings: `Evidence Status: INFERRED`, `evidence_state: INFERRED`, `NOT IDENTIFIED` as a finding state, `final_assessment: UNRESOLVED`, "overall patentability" in active decision schema, old negative-evidence rules. Distinguish `LEGACY_STATE_IN_ACTIVE_SCHEMA` (fail) from `LEGACY_TERM_IN_HISTORICAL_DOCUMENT` (permit — v1.5 reports and migration docs legitimately contain these).
2. **Root/package/install parity check** — canonical digest comparison for all active framework files.

### Git

Repository initialized before implementation (baseline = v1.5). The repo versions the source-of-truth tree; it does not replace it.

## Section 7 — Validation Plan (Tesla US433,700 v1.6 Rerun)

**Deliverables:**
- `report-tesla-us433700-e2e-v16.md` (in `Test-report-results/` and `invention-evaluation-engine/examples/tesla-us433700/`)
- **Validation Matrix** — a separate artifact (not buried in the report): criterion, expected invariant, evidence location, automated check, result
- **Proposition Ledger** — every proposition with its gate record:
  ```yaml
  proposition_ledger:
    - proposition_id: P-03-001
      skill: 03
      schema: performance_data
      gate:
        required: true
        executed: true
      outcome:
        evidence: ESTABLISHED | EXCLUDED
        work_state: ...
  ```
  Validation proves: `total propositions generated = propositions with gate record`.
- **Avenue Ledger** — per search proposition:
  ```yaml
  avenue_ledger:
    proposition_id: P-06-004
    avenues:
      - id: A1
        priority: 1
        status: COMPLETE
      - id: A2
        priority: 2
        status: BLOCKED
  ```
  Validation proves: all required avenues dispositioned AND sequence order preserved AND each avenue has an audit record.

### The 11 validation criteria

| # | Criterion | Expected invariant | Automated check |
|---|---|---|---|
| 1 | Evidence Sufficiency Gate exercised on every proposition | Every proposition has a gate record | Proposition Ledger count equality |
| 2 | Mandatory search-escalation loop exercised | Every required avenue dispositioned, order preserved, audit record present | Avenue Ledger required-state check |
| 3 | Correct state-level placement | `BLOCKED` is avenue-level; `EXHAUSTED` is proposition-level | Schema validation: fail on `proposition.work_state: BLOCKED` or `avenue.status: EXHAUSTED` |
| 4 | No legacy evidence states | No legacy work/evidence state emitted in an active finding object (NOT OBSERVED, NOT IDENTIFIED, INFERRED, NOT EVALUATED, CONTESTED, UNRESOLVED) | Anti-pattern scan of active files |
| 5 | Source-level provenance on every substantive assertion | Every substantive assertion (any factual statement in Established Findings, evidence summaries, source descriptions, or evidence-bearing tables that could materially affect a downstream conclusion) has `source_identity` + locator + exact-proposition support | Schema validator |
| 6 | Proposition-identity matching | IDs + versions stable across hand-offs; no schema/scope/text change without version increment | ID/version comparison across hand-off artifacts |
| 7 | No guessed content | No INFERRED/ASSUMED/APPROXIMATE/LIKELY/PROBABLY/ESTIMATED/GENERAL KNOWLEDGE/COMMON PRACTICE in audit objects without one of: exact source support / explicit analytical inference object / escalation / exclusion | Scan of underlying audit objects (not just final report) |
| 8 | Evidence vs. inference separated | Every analytical conclusion has a premise map; no premise is a work state | Structural premise-map validation |
| 9 | No unsupported UNRESOLVED terminal | `UNRESOLVED` absent as a terminal analytical conclusion | Scan |
| 10 | Hard stopping only on established evidence or genuine exhaustion | Only two valid stops: evidence sufficient → finding; or all avenues dispositioned → EXHAUSTED → excluded. Reject: search → didn't find → stop | Stop-mode audit |
| 11 | **Negative-control test** | Deliberately inject malformed propositions resembling the US7216695 failures ("Various SBIR awards…", "NAICS 334419 – inferred", "Research on UAV spray cooling…", "No international equivalents found.", "Commercial adoption not observed.") → ALL must fail the Sufficiency Gate → escalation or EXHAUSTED → EXCLUDED. **None may become a finding.** | Admission-pipeline run against injected propositions |

### Expected v1.6 outcomes on the Tesla corpus

| v1.5 outcome | v1.6 expected outcome |
|---|---|
| "1888–1890 journal full-text not accessible" | `BLOCKED` avenue with alternate access routes actually attempted and logged (Archive.org, Google Books, HathiTrust, periodical indexes — the attempts must be evidenced, not asserted); proposition dispositioned accordingly |
| Motivation "INFERRED" | Work state with the motivation-search ladder in the audit; if exhausted → proposition excluded from factual findings |
| "Unexpected result NOT IDENTIFIED" | Proposition requires performance-comparison schema → not established → Operational Audit, `barrier_type: insufficient_technical_demonstration` |
| Market sizing "NOT IDENTIFIED in primary source" | Excluded with `barrier_type: source_unavailable / insufficient_identity` |
| Commercial adoption "NOT OBSERVED" | Proposition "shield approach was commercially adopted" fails product-identity schema → Operational Audit; report states "could not be established from the completed evidence protocol" — never "no adoption was identified" |
| Report structure | Three areas; Executive Summary (if requested) ⊆ Established + Analytical |

## Files to change

1. `DIGEST.md`
2. `GLOSSARY.md`
3. `INDEX.md`
4. `PIPELINE_STATE.md`
5. `README.md`
6. `skill-01-invention-evaluation-overview/SKILL.md`
7. `skill-02-gather-invention-submission/SKILL.md` (minimal)
8. `skill-03-analyze-technology-fundamentals/SKILL.md`
9. `skill-04-conduct-patent-landscape/SKILL.md`
10. `skill-05-conduct-novelty-search/SKILL.md`
11. `skill-06-conduct-literature-search/SKILL.md`
12. `skill-07-analyze-market-opportunity/SKILL.md`
13. `skill-08-identify-partners/SKILL.md`
14. `skill-09-compile-report/SKILL.md`
15. `verify.sh` (legacy scan + parity check)
16. `invention-evaluation-engine/` package (mirror of all above)
17. Installed copy via `install.sh`
18. New: `docs/superpowers/specs/2026-08-14-invention-evaluation-framework-v16-design.md` (this file)
19. New: `Test-report-results/report-tesla-us433700-e2e-v16.md` + validation matrix + ledgers
20. New: `invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md`; update `quickstart-prompt.md`

## Validation standard

The v1.6 validation is not "Tesla produced a better report." It is:

> **The framework demonstrably refuses to admit unsupported propositions, deterministically escalates searches, preserves provenance across hand-offs, and rejects the exact classes of lazy evidence behavior that v1.5 permitted.**