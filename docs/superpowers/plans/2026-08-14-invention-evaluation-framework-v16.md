# Invention Evaluation Framework v1.6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the v1.5 evidence ontology with the v1.6 evidence-sufficiency architecture across the framework, then validate via a Tesla US433,700 rerun plus a negative-control test.

**Architecture:** The framework is a set of markdown skill files plus bash verification. The v1.6 control surface is `GLOSSARY.md` (three-layer epistemic architecture, Evidence Sufficiency Gate, Search Escalation Protocol, Proposition-Schema Registry, finding object) and `verify.sh` (legacy-terminology semantic scan + root/package/install parity). Skills 01–09 emit into that structure. The package (`invention-evaluation-engine/`) and installed copy (`~/.opencode/skills/`) are propagated artifacts, never independent sources of truth.

**Tech Stack:** Markdown skill files, bash (`verify.sh`), grep-based semantic checks, git. No code dependencies.

## Global Constraints

- **Governing principle:** "Unsupported assertions are errors. Missing evidence is a work queue, not an answer." Must appear at the top of DIGEST.md, GLOSSARY.md, and Skills 01/05/06/07/09.
- **Evidence layer:** only `CONFIRMED PRESENT` / `CONFIRMED ABSENT`. `CONFIRMED ABSENT` requires `absence_basis` (bounded_universe_definition, sufficiency_test) inside the finding object.
- **Work layer:** `NOT_STARTED` (engine-internal), `SEARCHING`, `ESCALATING`, `REQUIRES VERIFICATION`, `BLOCKED` (avenue-level), `EXHAUSTED` (proposition-level).
- **Analytical layer:** inference is never evidence. Factual assertion → `source_identity` + locator; analytical conclusion → premise_map + inference + rule_applied.
- **Anti-collapse invariants:** `EXHAUSTED ≠ CONFIRMED ABSENT`; `BLOCKED ≠ CONFIRMED ABSENT`; `REQUIRES VERIFICATION ≠ CONFIRMED PRESENT`; `INFERENCE ≠ EVIDENCE`; search completion is not evidence.
- **EXHAUSTED entry condition:** every required avenue ∈ {COMPLETE, BLOCKED, NOT_APPLICABLE} AND no required avenue = REQUIRES_VERIFICATION.
- **Atomic admission:** a proposition either fully passes the Sufficiency Gate or stays in the work queue. No "mostly supported."
- **Proposition-Schema Registry:** single authoritative source in GLOSSARY.md. Skills reference schema IDs; no schema may be duplicated or modified in a skill file.
- **Prohibited language** (and semantic equivalents) in factual findings: "Not found," "No X was identified," "No evidence of X exists," "appears absent," "there is no evidence that…," "apparently none," "likely not," "could not locate," "no known," "none identified," "no record was found," "Inferred," "Medium completeness." Allowed only in the Operational Audit describing search activity.
- **Legacy states** (NOT OBSERVED, NOT IDENTIFIED, INFERRED, NOT EVALUATED, CONTESTED, UNRESOLVED) may appear only in historical reports, migration documentation, and the GLOSSARY legacy-mapping table — never as active semantics.
- **Parity:** root skill/docs files must be byte-identical to `invention-evaluation-engine/` copies (verified by sha256).
- **Report architecture:** three areas — Established Findings / Analytical Conclusions (with premise maps) / Operational Audit (with barrier_type). Executive Summary ⊆ Established Findings + Analytical Conclusions.
- **UNRESOLVED may not appear as a terminal analytical conclusion.** Three outcomes only: more work → work layer; all work exhausted → exclude proposition; supported evidence → analytical conclusion permitted.

---

### Task 1: GLOSSARY.md — v1.6 control surface rewrite

**Files:**
- Rewrite: `GLOSSARY.md` (root; package copy updated in Task 14)

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-08-14-invention-evaluation-framework-v16-design.md` (the canonical spec — all blocks below are copied from it verbatim)
- Produces: the single source of truth that every skill references: three-layer architecture, Sufficiency Gate, avenue protocol, Proposition-Schema Registry, finding object, barrier_type, prohibited language, updated dependent constructs

- [ ] **Step 1: Replace the "Evidence Status — Global Ontology" section (lines 32–59) with the three-layer architecture**

Replace the 7-state table and the Negative Evidence Coverage Rule with:

```markdown
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
```

- [ ] **Step 2: Add the Evidence Sufficiency Gate section (after the three-layer architecture)**

```markdown
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
```

- [ ] **Step 3: Add the Proposition-Schema Registry section**

```markdown
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
```

**Row non-existence rule:** a finding row does not exist unless every required schema field is populated with an exact identifier. "Various SBIR awards…" fails `market_relevance_award` (no award_id). "NAICS 334419 – INFERRED" fails `naics_classification` (no taxonomy_source, no edition_year, no basis). "Research on UAV spray cooling…" fails `literature_disclosure` (no publication identity, no demonstrated result).
```

- [ ] **Step 4: Add the Search Escalation Protocol section**

```markdown
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
```

- [ ] **Step 5: Add the Finding Object section**

```markdown
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
```

- [ ] **Step 6: Add the Report Architecture section**

```markdown
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
```

- [ ] **Step 7: Update dependent constructs to the new vocabulary**

In the existing sections, replace every legacy evidence-state reference:

- **Obviousness Evidence Object** (lines ~161–229): `evidence_state: [7-state list]` → `evidence_state: [CONFIRMED PRESENT | CONFIRMED ABSENT]`; `final_assessment: [... or UNRESOLVED ...]` → `final_assessment: [Limited / Moderate / High obviousness risk]` with the note "UNRESOLVED is not a terminal state: if motivation, expectation, or the causal bridge cannot be evidenced, the proposition is excluded from factual findings and recorded in the Operational Audit with barrier_type"; `coverage:` block → `search_escalation:` block (avenue checklist per the protocol); `motivation.status: [... INFERRED ...]` → `motivation.status: [GROUNDED | PARTIALLY GROUNDED | RECONCILIATION REQUIRED]` plus `motivation_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]`; knowledge-decomposition flags `NOT OBSERVED (coverage)` → `NOT ESTABLISHED (avenue record)`.
- **Motivation Object** (lines ~233–262): derivation table row "Only inferred → INFERRED" → "Only inferred → motivation not established; proposition enters work layer (SEARCHING/ESCALATING) until direct or analogous evidence is found or avenues are exhausted".
- **Causal Bridge Test** (lines ~266–302): `bridge_status: [TRAVERSED | UNTRAVERSED | UNRESOLVED]` → `bridge_status: [TRAVERSED | UNTRAVERSED]` plus `bridge_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]`; the sentence "UNRESOLVED — the default when motivation is INFERRED or application is NOT OBSERVED" → "When motivation or application evidence is insufficient, the bridge is not assessed as a conclusion; the proposition enters the work layer until evidence is established or avenues are exhausted."
- **Decision Matrix** (lines ~306–372): "DECISION + UNCERTAINTY" terminal → "EVIDENCE SUFFICIENCY GATE → FINDING (CONFIRMED PRESENT/ABSENT) or WORK QUEUE (escalation)".
- **Multidimensional Decision Output** (lines ~376–392): replace "Obviousness risk ... plus UNRESOLVED when ... cannot be evidenced" → "Obviousness risk: Limited / Moderate / High — or 'not established' (proposition excluded, see Operational Audit)"; "Historical disclosure coverage: Complete / Incomplete / Not evaluated" → "Historical disclosure coverage: Established / Not established (see Operational Audit)"; "Commercial adoption evidence: Present / Not observed / Confirmed absent" → "Commercial adoption evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / Not established (see Operational Audit)"; "Market sizing: Sufficient / Insufficient / Not evaluated" → "Market sizing: Established / Not established (see Operational Audit)".

- [ ] **Step 8: Verify the rewrite**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
# No legacy states as active semantics (the legacy-mapping table is exempted by markers)
grep -nE "evidence_state: (NOT OBSERVED|NOT IDENTIFIED|INFERRED|NOT EVALUATED|CONTESTED)" GLOSSARY.md || echo "PASS: no legacy evidence_state assignments"
grep -nE "bridge_status: .*UNRESOLVED|final_assessment: .*UNRESOLVED" GLOSSARY.md || echo "PASS: no UNRESOLVED terminal states"
grep -n "Negative Evidence Coverage Rule" GLOSSARY.md || echo "PASS: Negative Evidence Coverage Rule removed"
grep -n "Proposition-Schema Registry" GLOSSARY.md && grep -n "Evidence Sufficiency Gate" GLOSSARY.md && grep -n "Search Escalation Protocol" GLOSSARY.md && grep -n "Finding Object" GLOSSARY.md && grep -n "Report Architecture" GLOSSARY.md
```
Expected: all PASS lines and all five section headers found.

- [ ] **Step 9: Commit**

```bash
git add GLOSSARY.md
git commit -m "feat(v1.6): GLOSSARY control surface — three-layer architecture, sufficiency gate, escalation protocol, schema registry, finding object"
```

---

### Task 2: verify.sh — v1.6 validation machinery

**Files:**
- Rewrite: `verify.sh` (root; package copy updated in Task 14)

**Interfaces:**
- Consumes: the v1.6 vocabulary from Task 1
- Produces: `./verify.sh` exit code 0 = v1.6 compliant; used as the test harness for every subsequent task

- [ ] **Step 1: Write the failing test — the legacy scan must detect v1.5 files**

The current tree is still v1.5, so the new scanner must FAIL on it. Write the new `verify.sh`:

```bash
#!/usr/bin/env bash
set -uo pipefail

# Invention Evaluation Engine — v1.6 install verifier
# Usage: ./verify.sh [--path /path/to/invention-evaluation-engine]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$SCRIPT_DIR/invention-evaluation-engine"

if [ "${1:-}" = "--path" ]; then
  TARGET="${2:?--path requires a directory argument}"
fi

FAIL=0
check() {
  local desc="$1" file="$2"
  if [ -f "$file" ]; then
    echo "  [PASS] $desc"
  else
    echo "  [FAIL] $desc — missing: $file"
    FAIL=1
  fi
}

echo "Verifying invention-evaluation-engine at: $TARGET"
echo ""

check "engine SKILL.md" "$TARGET/SKILL.md"
check "sub-skill 01" "$TARGET/skills/skill-01-invention-evaluation-overview/SKILL.md"
check "sub-skill 02" "$TARGET/skills/skill-02-gather-invention-submission/SKILL.md"
check "sub-skill 03" "$TARGET/skills/skill-03-analyze-technology-fundamentals/SKILL.md"
check "sub-skill 04" "$TARGET/skills/skill-04-conduct-patent-landscape/SKILL.md"
check "sub-skill 05" "$TARGET/skills/skill-05-conduct-novelty-search/SKILL.md"
check "sub-skill 06" "$TARGET/skills/skill-06-conduct-literature-search/SKILL.md"
check "sub-skill 07" "$TARGET/skills/skill-07-analyze-market-opportunity/SKILL.md"
check "sub-skill 08" "$TARGET/skills/skill-08-identify-partners/SKILL.md"
check "sub-skill 09" "$TARGET/skills/skill-09-compile-report/SKILL.md"
check "docs/DIGEST.md" "$TARGET/docs/DIGEST.md"
check "docs/GLOSSARY.md" "$TARGET/docs/GLOSSARY.md"
check "docs/INDEX.md" "$TARGET/docs/INDEX.md"
check "docs/PIPELINE_STATE.md" "$TARGET/docs/PIPELINE_STATE.md"
check "example submission" "$TARGET/examples/tesla-us433700/submission.md"
check "example quickstart prompt" "$TARGET/examples/tesla-us433700/quickstart-prompt.md"

for f in "$TARGET/SKILL.md" "$TARGET"/skills/skill-*/SKILL.md; do
  if [ -f "$f" ]; then
    if ! grep -q '^name:' "$f" || ! grep -q '^description:' "$f"; then
      echo "  [FAIL] frontmatter missing name/description in $f"
      FAIL=1
    fi
  fi
done

echo ""
echo "--- v1.6 legacy-terminology semantic scan (active schema files) ---"
# Active files: engine SKILL + sub-skills + docs. Historical artifacts
# (Test-report-results/, examples/, docs/superpowers/) are exempt.
ACTIVE_FILES=(
  "$TARGET/SKILL.md"
  "$TARGET"/skills/skill-*/SKILL.md
  "$TARGET/docs/DIGEST.md"
  "$TARGET/docs/GLOSSARY.md"
  "$TARGET/docs/INDEX.md"
  "$TARGET/docs/PIPELINE_STATE.md"
)

# Anti-patterns: legacy states used as ACTIVE semantics (not in the
# GLOSSARY legacy-mapping table, which is delimited by markers).
LEGACY_ANTIPATTERNS=(
  'evidence_state: NOT OBSERVED'
  'evidence_state: NOT IDENTIFIED'
  'evidence_state: INFERRED'
  'evidence_state: NOT EVALUATED'
  'evidence_state: CONTESTED'
  'Evidence Status: INFERRED'
  'bridge_status: .*UNRESOLVED'
  'final_assessment: .*UNRESOLVED'
  'status: INFERRED'
  'completeness: MEDIUM'
  'Negative Evidence Coverage Rule'
  'overall patentability'
)

for f in "${ACTIVE_FILES[@]}"; do
  [ -f "$f" ] || continue
  # Skip the delimited legacy-mapping table inside GLOSSARY
  if [[ "$f" == *GLOSSARY.md ]]; then
    awk '/<!-- v1.6-legacy-mapping -->/{skip=1} /<!-- \/v1.6-legacy-mapping -->/{skip=0; next} !skip' "$f" > /tmp/v16-glossary-scan.txt
    SCAN_FILE=/tmp/v16-glossary-scan.txt
  else
    SCAN_FILE="$f"
  fi
  for pat in "${LEGACY_ANTIPATTERNS[@]}"; do
    if grep -qE "$pat" "$SCAN_FILE"; then
      echo "  [FAIL] LEGACY_STATE_IN_ACTIVE_SCHEMA: '$pat' in $f"
      FAIL=1
    fi
  done
done
echo "  (legacy terms in historical reports / migration docs are permitted)"

echo ""
echo "--- v1.6 root/package parity check ---"
# root path | package path. Root holds docs at top level and skills in
# skill-XX/ dirs; the package holds them under docs/ and skills/. The engine
# SKILL.md is package-only (no root counterpart) and is not parity-checked.
ROOT_DIR="$SCRIPT_DIR"
PARITY_PAIRS=(
  "DIGEST.md|docs/DIGEST.md"
  "GLOSSARY.md|docs/GLOSSARY.md"
  "INDEX.md|docs/INDEX.md"
  "PIPELINE_STATE.md|docs/PIPELINE_STATE.md"
  "skill-01-invention-evaluation-overview/SKILL.md|skills/skill-01-invention-evaluation-overview/SKILL.md"
  "skill-02-gather-invention-submission/SKILL.md|skills/skill-02-gather-invention-submission/SKILL.md"
  "skill-03-analyze-technology-fundamentals/SKILL.md|skills/skill-03-analyze-technology-fundamentals/SKILL.md"
  "skill-04-conduct-patent-landscape/SKILL.md|skills/skill-04-conduct-patent-landscape/SKILL.md"
  "skill-05-conduct-novelty-search/SKILL.md|skills/skill-05-conduct-novelty-search/SKILL.md"
  "skill-06-conduct-literature-search/SKILL.md|skills/skill-06-conduct-literature-search/SKILL.md"
  "skill-07-analyze-market-opportunity/SKILL.md|skills/skill-07-analyze-market-opportunity/SKILL.md"
  "skill-08-identify-partners/SKILL.md|skills/skill-08-identify-partners/SKILL.md"
  "skill-09-compile-report/SKILL.md|skills/skill-09-compile-report/SKILL.md"
)
for pair in "${PARITY_PAIRS[@]}"; do
  root_rel="${pair%%|*}"
  pkg_rel="${pair##*|}"
  root_file="$ROOT_DIR/$root_rel"
  pkg_file="$TARGET/$pkg_rel"
  if [ -f "$root_file" ] && [ -f "$pkg_file" ]; then
    if [ "$(sha256sum "$root_file" | cut -d' ' -f1)" = "$(sha256sum "$pkg_file" | cut -d' ' -f1)" ]; then
      echo "  [PASS] parity: $root_rel ↔ $pkg_rel"
    else
      echo "  [FAIL] parity mismatch: $root_rel ↔ $pkg_rel (root ≠ package)"
      FAIL=1
    fi
  else
    echo "  [FAIL] parity: missing file for $root_rel ↔ $pkg_rel (root=$root_file pkg=$pkg_file)"
    FAIL=1
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
```

- [ ] **Step 2: Run the verifier to confirm it fails on the v1.5 tree**

Run: `cd /home/forsythe/Downloads/invention-evaluation-framework && ./verify.sh`
Expected: FAIL — legacy anti-patterns detected in the v1.5 skill files and docs (e.g., `evidence_state: NOT OBSERVED` in skill-05, `Negative Evidence Coverage Rule` in DIGEST/GLOSSARY), and parity FAIL for files not yet mirrored. This proves the scanner works.

- [ ] **Step 3: Commit**

```bash
git add verify.sh
git commit -m "feat(v1.6): verify.sh — legacy-terminology semantic scan + root/package parity check"
```

---

### Task 3: DIGEST.md — non-negotiables rewrite

**Files:**
- Rewrite: `DIGEST.md` (root; package copy updated in Task 14)

**Interfaces:**
- Consumes: Task 1 vocabulary
- Produces: the 5-minute read that every skill's governing principle references

- [ ] **Step 1: Replace the non-negotiables list**

Keep items 1–2, 4–8, 10–11, 14–15, 17–22 as-is (they remain valid). Apply these changes:

- **Item 12** (evidence-state discipline) → replace with the three-layer hierarchy:
  ```markdown
  12. **Three-layer epistemic architecture.** Evidence layer: CONFIRMED PRESENT / CONFIRMED ABSENT only. Work layer: NOT_STARTED (internal) / SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED (avenue-level) / EXHAUSTED (proposition-level). Analytical layer: evidence → inference → conclusion; inference is never evidence. Anti-collapse invariants: EXHAUSTED ≠ CONFIRMED ABSENT; BLOCKED ≠ CONFIRMED ABSENT; REQUIRES VERIFICATION ≠ CONFIRMED PRESENT; INFERENCE ≠ EVIDENCE; search completion is not evidence. CONFIRMED ABSENT requires a bounded evidence universe + absence_basis.
  ```
- **Item 13** (Negative Evidence Coverage Rule) → replace with:
  ```markdown
  13. **Evidence Sufficiency & Search Escalation Rule.** A proposition enters the report only through the Evidence Sufficiency Gate (schema-driven, atomic). When the gate fails, the search escalates through the skill's fixed avenue checklist (deterministic priority). EXHAUSTED is a proposition-level termination state emitted only when every required avenue is COMPLETE / BLOCKED / NOT_APPLICABLE (no avenue left REQUIRES_VERIFICATION). EXHAUSTED never constitutes evidence. Unestablished propositions are omitted from factual findings and retained in the Operational Audit with barrier_type.
  ```
- **Item 16** ("Insufficient evidence is a valid, required output") → replace with:
  ```markdown
  16. **Missing evidence is a work queue, not an answer.** Do not fill a gap with a plausible-sounding guess and do not report "not found" as a conclusion. Escalate the search; if avenues are exhausted, exclude the proposition from factual findings and record it in the Operational Audit. Unsourced quantitative claims are omitted.
  ```
- **Item 23** (Causal Bridge Test) → change `bridge_status ... UNRESOLVED (default when motivation is INFERRED or application is NOT OBSERVED)` to `bridge_status: TRAVERSED / UNTRAVERSED; when motivation or application evidence is insufficient, the bridge is not assessed as a conclusion — the proposition enters the work layer (see GLOSSARY.md)`.
- **Item 9** (motivation) → change "Ungrounded motivation → INFERRED → obviousness finding is UNRESOLVED" to "Ungrounded motivation → motivation not established → the obviousness proposition enters the work layer until evidence is established or avenues are exhausted".
- **Item 17** (counterfactual-exclusivity) → change "replace with 'strongest identified pathway'" stays; remove any "NOT OBSERVED" phrasing → "alternatives not established (see Operational Audit)".
- **Add at the top of the non-negotiables list:**
  ```markdown
  0. **Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. A proposition is either admitted as an evidence-backed finding or it remains in the work queue — there is no third category.
  ```

- [ ] **Step 2: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "Governing principle" DIGEST.md
grep -n "Evidence Sufficiency & Search Escalation Rule" DIGEST.md
grep -n "Negative Evidence Coverage Rule" DIGEST.md || echo "PASS: old rule removed"
grep -nE "INFERRED|UNRESOLVED|NOT OBSERVED" DIGEST.md || echo "PASS: no legacy terminal states"
```
Expected: governing principle + new rule present; old rule and legacy terminal states absent.

- [ ] **Step 3: Commit**

```bash
git add DIGEST.md
git commit -m "feat(v1.6): DIGEST — governing principle, evidence sufficiency & search escalation rule"
```

---

### Task 4: skill-01 overview + engine SKILL.md — vocabulary and proposition-identity preservation

**Files:**
- Modify: `skill-01-invention-evaluation-overview/SKILL.md` (root)
- Modify: `invention-evaluation-engine/SKILL.md` (root package; installed copy in Task 14)

**Interfaces:**
- Consumes: Task 1 vocabulary
- Produces: the hand-off rule that all skills inherit: proposition-identity preservation

- [ ] **Step 1: Update skill-01**

In `skill-01-invention-evaluation-overview/SKILL.md`:
- Add at the top of the "Core principle" section, before the existing paragraph:
  ```markdown
  **Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.
  ```
- Replace the "Core principle" paragraph: change "Every proposition carries the evidence grade it was established with (see GLOSSARY.md — Evidence → Inference → Conclusion firewall)" to:
  ```markdown
  This pipeline is an **evidence-constrained invention reasoning engine**, not a collection of research prompts. The governing rule, enforced at every stage: **nothing downstream is allowed to promote an inference into a fact, and no proposition enters the report except through the Evidence Sufficiency Gate.** Every proposition carries a stable `proposition_id` + `proposition_version` and the evidence state it was established with (see GLOSSARY.md — Epistemic Architecture). The framework's job is to separate *what the evidence establishes* from *what the analyst wants to conclude* — and to prevent the two from merging.
  ```
- Replace execution step 4: "Each routed output must preserve its evidence grades — never strip or upgrade them at hand-off." → "Each routed output must preserve proposition identity: `proposition_id` + `proposition_version` + evidence state. Never strip, upgrade, or silently re-scope a proposition at hand-off; any refinement requires a version increment."
- Add to the Boundary section: "Unestablished propositions are work-queue items, not findings. See GLOSSARY.md — Evidence Sufficiency Gate."

- [ ] **Step 2: Update engine SKILL.md**

In `invention-evaluation-engine/SKILL.md`:
- Add at the top of the "What this is" section:
  ```markdown
  **Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.
  ```
- Replace the "What this is" paragraph's evidence-grade sentence: "Every proposition carries the evidence grade it was established with (see `docs/GLOSSARY.md`)." → "Every proposition carries a stable `proposition_id` + `proposition_version` and the evidence state it was established with (see `docs/GLOSSARY.md` — Epistemic Architecture). Nothing enters the final report except through the Evidence Sufficiency Gate."
- Replace execution step 3 (Evidence-grade preservation): "carry each proposition with the evidence grade it was established with (CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED) plus any coverage objects. Never upgrade or strip grades." → "carry each proposition with its `proposition_id`, `proposition_version`, and evidence state (CONFIRMED PRESENT / CONFIRMED ABSENT) plus its avenue records. Never upgrade, strip, or re-scope a proposition at hand-off; any refinement requires a version increment. Unestablished propositions remain in the work queue with their search records."
- Update the reference-docs line for GLOSSARY: "full terminology, evidence ontology, decision matrix" → "full terminology, three-layer epistemic architecture, sufficiency gate, escalation protocol, schema registry".

- [ ] **Step 3: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "proposition_id" skill-01-invention-evaluation-overview/SKILL.md invention-evaluation-engine/SKILL.md
grep -nE "NOT OBSERVED|INFERRED|CONTESTED" skill-01-invention-evaluation-overview/SKILL.md invention-evaluation-engine/SKILL.md || echo "PASS: no legacy states"
```
Expected: proposition_id present in both; no legacy states.

- [ ] **Step 4: Commit**

```bash
git add skill-01-invention-evaluation-overview/SKILL.md invention-evaluation-engine/SKILL.md
git commit -m "feat(v1.6): skill-01 + engine — proposition-identity preservation vocabulary"
```

---

### Task 5: skill-02 gather-invention-submission — minimal update

**Files:**
- Modify: `skill-02-gather-invention-submission/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 vocabulary
- Produces: intake that records disclosure timing without legacy negative states

- [ ] **Step 1: Update the disclosure-timing paragraph**

In the "Mandatory — disclosure timing" paragraph, replace:
"record that as "CONFIRMED ABSENT (per inventor statement)" rather than leaving the field blank — a blank field and a confirmed "none" are not the same thing for audit purposes. **Distinguish the two negative states:** an inventor's direct statement of no disclosure is CONFIRMED ABSENT (per that source); a search that found no disclosure is NOT OBSERVED (coverage may be insufficient to establish historical absence). Never upgrade a search-based "not found" into "confirmed absent.""

with:
"record that as "CONFIRMED ABSENT (per inventor statement)" — the bounded universe is the inventor's own statement, with `absence_basis` noted — rather than leaving the field blank; a blank field and a confirmed "none" are not the same thing for audit purposes. **Distinguish the two cases:** an inventor's direct statement of no disclosure is CONFIRMED ABSENT (bounded universe: inventor statement, single source); a search that found no disclosure is a search-result record (avenue metadata) — it establishes nothing about the world and never upgrades to CONFIRMED ABSENT. If a search-based absence is needed, it must go through the Evidence Sufficiency Gate with a bounded universe."

- [ ] **Step 2: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "NOT OBSERVED" skill-02-gather-invention-submission/SKILL.md || echo "PASS: no legacy state"
grep -n "absence_basis" skill-02-gather-invention-submission/SKILL.md
```
Expected: no NOT OBSERVED; absence_basis present.

- [ ] **Step 3: Commit**

```bash
git add skill-02-gather-invention-submission/SKILL.md
git commit -m "feat(v1.6): skill-02 — disclosure timing without legacy negative states"
```

---

### Task 6: skill-03 analyze-technology-fundamentals — regulatory regime schema, exact classifications

**Files:**
- Modify: `skill-03-analyze-technology-fundamentals/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 registry (`regulatory_regime`, `performance_data` schemas)
- Produces: technology profile whose regulatory and classification outputs are schema-valid

- [ ] **Step 1: Update the execution steps**

- **Step 5 (Unexpected-result gate):** replace "(CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / INFERRED / CONTESTED). If NOT IDENTIFIED, flag it as an evidence gap in the final report." → "(CONFIRMED PRESENT / CONFIRMED ABSENT — or not established, see Operational Audit). If the performance data proposition cannot be established, it enters the work queue: escalate through the `performance_data` schema avenues; if exhausted, record in the Operational Audit with `barrier_type: insufficient_technical_demonstration`."
- **Step 6 (Regulatory burden):** replace "Estimate Low/Med/High per relevant jurisdiction, with the governing body cited." → "Estimate Low/Med/High per relevant jurisdiction using the `regulatory_regime` schema: governing statute/regulation (exact identifier) + why the technology falls inside/outside it. A regulatory rating without the governing regime is not a finding — it is an unestablished proposition."
- **Step 8 (Classification seed):** replace "Derive an initial IPC/CPC candidate set from the idea description" → "Derive an initial IPC/CPC candidate set from the idea description, each candidate with its exact code, official title, and source (official classification authority). A guessed classification is not a finding — candidates are hypotheses for the landscape search, not established classifications."
- **Add a new step after step 8:** "**Proposition ledger.** Register every substantive proposition this skill produces (performance data, regulatory regime, classification candidates) with a `proposition_id` + `proposition_version` + schema reference, per GLOSSARY.md."

- [ ] **Step 2: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "regulatory_regime" skill-03-analyze-technology-fundamentals/SKILL.md
grep -n "proposition_id" skill-03-analyze-technology-fundamentals/SKILL.md
grep -nE "NOT OBSERVED|NOT IDENTIFIED|INFERRED|CONTESTED" skill-03-analyze-technology-fundamentals/SKILL.md || echo "PASS: no legacy states"
```
Expected: regulatory_regime + proposition_id present; no legacy states.

- [ ] **Step 3: Commit**

```bash
git add skill-03-analyze-technology-fundamentals/SKILL.md
git commit -m "feat(v1.6): skill-03 — regulatory regime schema, exact classifications, proposition ledger"
```

---

### Task 7: skill-04 conduct-patent-landscape — avenue records for negative findings

**Files:**
- Modify: `skill-04-conduct-patent-landscape/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 escalation protocol
- Produces: landscape findings whose negative results carry avenue records, not coverage objects

- [ ] **Step 1: Update step 8 (Coverage on negative landscape findings)**

Replace:
"8. **Coverage on negative landscape findings.** If the landscape finding is negative (e.g., "no filings found in jurisdiction X," "no assignee found for this classification"), treat it as a negative evidence finding: carry a coverage object (scope, temporal scope, databases searched, completeness LOW/MEDIUM/HIGH/EXHAUSTIVE, limitations). Coverage is metadata, not evidence — it never upgrades a "not observed" to "confirmed absent." Single-source landscaping is LOW coverage; state it as such rather than reporting absence as fact."

with:
"8. **Negative landscape findings go through the escalation protocol.** If the landscape search returns no filings for a proposition (e.g., "no filings found in jurisdiction X"), the proposition does not become a finding. Run the skill's avenue checklist (primary source → classification search → citation expansion → terminology expansion → alternate database → organizational records → jurisdiction-specific sources → independent corroboration), logging each avenue record. Only when every required avenue is dispositioned (COMPLETE / BLOCKED / NOT_APPLICABLE) may the proposition be marked EXHAUSTED — and EXHAUSTED is not evidence: the proposition is excluded from factual findings and recorded in the Operational Audit with `barrier_type` (e.g., `insufficient_search_completion`). Single-source landscaping is one avenue, not exhaustion. CONFIRMED ABSENT additionally requires a bounded universe + absence_basis."

- [ ] **Step 2: Add the avenue checklist to the skill**

Add after step 8:
"9. **Avenue checklist (mandatory for every negative landscape proposition).** Use the default avenue template from GLOSSARY.md (Search Escalation Protocol), customized for landscape propositions: A1 primary patent database (e.g., WIPO PatentScope), A2 classification search (CPC/IPC), A3 citation expansion, A4 terminology expansion, A5 alternate database (e.g., Espacenet, Derwent), A6 organizational records (assignee filings), A7 jurisdiction-specific sources, A8 independent corroboration. Each avenue carries an `avenue_record` with searches_run, sources_consulted, relevant_results, exclusions, limitations, completion_basis."

Renumber the following steps (9→10, 10→11) accordingly.

- [ ] **Step 3: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "avenue" skill-04-conduct-patent-landscape/SKILL.md
grep -nE "coverage object|NOT OBSERVED|NOT IDENTIFIED" skill-04-conduct-patent-landscape/SKILL.md || echo "PASS: no legacy coverage/state language"
```
Expected: avenue references present; legacy coverage-object language absent.

- [ ] **Step 4: Commit**

```bash
git add skill-04-conduct-patent-landscape/SKILL.md
git commit -m "feat(v1.6): skill-04 — avenue records for negative landscape findings"
```

---

### Task 8: skill-05 conduct-novelty-search — the largest skill change

**Files:**
- Modify: `skill-05-conduct-novelty-search/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 registry (`prior_art_disclosure`), escalation protocol, updated obviousness/motivation/bridge constructs
- Produces: novelty findings with no legacy terminal states; the model for Skills 06–08

- [ ] **Step 1: Update the Causal Bridge Test block (lines 67–94)**

Replace `bridge_status: [TRAVERSED | UNTRAVERSED | UNRESOLVED]` with `bridge_status: [TRAVERSED | UNTRAVERSED]` and add `bridge_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]`.

Replace the bridge_status sentence (line 94):
"**bridge_status:** TRAVERSED = evidence shows a skilled person would cross the bridge (obviousness strengthens); UNTRAVERSED = evidence shows the bridge was not reasonably crossable (non-obviousness argument); **UNRESOLVED = the default when motivation is INFERRED or application is NOT OBSERVED** — neither direction evidenced."

with:
"**bridge_status:** TRAVERSED = evidence shows a skilled person would cross the bridge (obviousness strengthens); UNTRAVERSED = evidence shows the bridge was not reasonably crossable (non-obviousness argument). **When motivation or application evidence is insufficient, the bridge is not assessed as a conclusion** — the proposition enters the work layer (bridge_work_state: SEARCHING / ESCALATING / REQUIRES VERIFICATION / EXHAUSTED) until evidence is established or the avenue checklist is exhausted. UNRESOLVED is not a terminal state."

- [ ] **Step 2: Update the Obviousness Evidence Object (lines 96–159)**

- `knowledge_decomposition:` flags: `[CONFIRMED PRESENT (source) | NOT OBSERVED (coverage) | ...]` → `[CONFIRMED PRESENT (source) | NOT ESTABLISHED (avenue record) | ...]`
- `motivation_to_combine: [GROUNDED | PARTIALLY GROUNDED | INFERRED | RECONCILIATION REQUIRED]` → `motivation_to_combine: [GROUNDED | PARTIALLY GROUNDED | RECONCILIATION REQUIRED]` plus `motivation_work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]`
- `coverage:` block (lines 112–118) → `search_escalation:` block (avenue checklist per GLOSSARY.md Search Escalation Protocol)
- `motivation:` object `status: [GROUNDED | PARTIALLY GROUNDED | INFERRED | RECONCILIATION REQUIRED]` → `status: [GROUNDED | PARTIALLY GROUNDED | RECONCILIATION REQUIRED]` plus `work_state: [SEARCHING | ESCALATING | REQUIRES VERIFICATION | EXHAUSTED]`
- `technical_effect.evidence: [7-state list]` → `[CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (avenue record)]`
- `evidence_state: [7-state list]` → `evidence_state: [CONFIRMED PRESENT | CONFIRMED ABSENT]`
- `final_assessment: [Limited / Moderate / High obviousness risk — or UNRESOLVED when ...]` → `final_assessment: [Limited / Moderate / High obviousness risk]` plus the note: "If motivation, expectation-of-success, or the causal bridge cannot be evidenced, the obviousness proposition is not assessed as a conclusion — it is excluded from factual findings and recorded in the Operational Audit with barrier_type."

- [ ] **Step 3: Update the gates list (lines 161–168)**

- **Motivation object gate:** "Paths with only INFERRED motivation cannot support anything stronger than an UNRESOLVED obviousness finding." → "Paths with only inferred motivation (no direct or analogous source) cannot support an obviousness finding: the motivation proposition enters the work layer and escalates through the avenue checklist; if exhausted, the obviousness proposition is excluded from factual findings (see Operational Audit)."
- **Causal Bridge Test gate:** "bridge_status defaults to UNRESOLVED when motivation is INFERRED or application is NOT OBSERVED." → "bridge_status is only TRAVERSED or UNTRAVERSED; when motivation or application evidence is insufficient, the bridge proposition enters the work layer."
- **Coverage gate:** "Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries a coverage object (scope, temporal scope, source domains, depth, completeness, limitations). Coverage never changes evidence state." → "Every negative search result is recorded as avenue metadata in the avenue checklist. Coverage objects are replaced by avenue records. Search completion is not evidence."
- **Known principle ≠ obvious application:** "If the specific application is NOT OBSERVED/NOT IDENTIFIED in the record, weaken the obviousness finding's confidence accordingly." → "If the specific application is not established in the record, the application proposition enters the work layer; if avenues are exhausted, the obviousness proposition is excluded from factual findings."

- [ ] **Step 4: Update steps 9, 11, and the Boundary**

- **Step 9 (Unexpected-result check):** "If NOT IDENTIFIED, flag as evidence gap" → "If the performance-comparison data proposition cannot be established, it enters the work queue (escalate through the `performance_data` schema avenues); if exhausted, record in the Operational Audit with `barrier_type: insufficient_technical_demonstration`."
- **Step 11 (Score per gate):** replace all `Evidence status: [7-state list]` with `Evidence status: [CONFIRMED PRESENT | CONFIRMED ABSENT | NOT ESTABLISHED (see Operational Audit)]`; replace "(Limited/Moderate/High — or UNRESOLVED)" with "(Limited/Moderate/High — or not established, see Operational Audit)".
- **Boundary — Evidence firewall:** "an INFERRED or NOT OBSERVED proposition cannot later be cited as CONFIRMED ABSENT or CONFIRMED PRESENT" → "an unestablished proposition (work state EXHAUSTED, BLOCKED, or REQUIRES VERIFICATION) cannot later be cited as CONFIRMED PRESENT or CONFIRMED ABSENT; it can only be cited as an unestablished proposition with its avenue records."
- **Add to the top of the Execution section:** "**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. Every prior-art proposition uses the `prior_art_disclosure` schema from GLOSSARY.md; a finding row does not exist unless every required schema field is populated."

- [ ] **Step 5: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -nE "UNRESOLVED|INFERRED|NOT OBSERVED|NOT IDENTIFIED|CONTESTED|coverage object" skill-05-conduct-novelty-search/SKILL.md || echo "PASS: no legacy terminal states"
grep -n "prior_art_disclosure" skill-05-conduct-novelty-search/SKILL.md
grep -n "search_escalation" skill-05-conduct-novelty-search/SKILL.md
grep -n "Governing principle" skill-05-conduct-novelty-search/SKILL.md
```
Expected: no legacy states; prior_art_disclosure, search_escalation, governing principle present.

- [ ] **Step 6: Commit**

```bash
git add skill-05-conduct-novelty-search/SKILL.md
git commit -m "feat(v1.6): skill-05 — prior-art schema, sufficiency gate, avenue escalation, no UNRESOLVED terminal"
```

---

### Task 9: skill-06 conduct-literature-search — paper schema and avenue records

**Files:**
- Modify: `skill-06-conduct-literature-search/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 registry (`literature_disclosure`), escalation protocol
- Produces: literature findings with publication identity, no legacy negative states

- [ ] **Step 1: Replace step 4 (flagged-item capture)**

Replace:
"4. For flagged items, capture title, date, key finding, and a relevance note stating specifically which element of the invention it touches — a generic "seems related" note is not usable downstream."

with:
"4. For flagged items, capture the full `literature_disclosure` schema from GLOSSARY.md: authors, title, venue, date, DOI/report number, URL, experimental system, cooling/technology, application, what was actually demonstrated, and a relevance note stating specifically which element of the invention it touches. A row without publication identity (authors, title, venue, date, DOI) does not exist. A generic "seems related" note is not usable downstream."

- [ ] **Step 2: Replace steps 7–8 (evidence-state discipline + coverage)**

Replace step 7 (the 7-state ontology list) and step 8 (coverage object) with:

"7. **Evidence-state discipline (v1.6).** Evidence layer: CONFIRMED PRESENT / CONFIRMED ABSENT only. Work layer: SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED (avenue) / EXHAUSTED (proposition). A search that returns nothing is avenue metadata, not evidence. CONFIRMED ABSENT requires a bounded universe + absence_basis. See GLOSSARY.md — Epistemic Architecture.
8. **Negative literature findings go through the escalation protocol.** If a proposition (e.g., "no pre-filing publication discloses the claimed mechanism") is not established, run the skill's avenue checklist (A1 primary source search → A2 classification search → A3 citation expansion → A4 terminology expansion → A5 alternate database → A6 organizational records → A7 jurisdiction-specific sources → A8 independent corroboration), logging each avenue_record. Only when every required avenue is dispositioned may the proposition be marked EXHAUSTED — and EXHAUSTED is not evidence: the proposition is excluded from factual findings and recorded in the Operational Audit with barrier_type. State the databases and date ranges actually searched in each avenue record (e.g., "IEEE Xplore 1880–1900, Google Scholar full range, domain: electrical engineering history")."

- [ ] **Step 3: Update step 8 (known principle ≠ obvious application) and add governing principle**

- Renumber the second "8." (known principle) to "9." and change "record the principle as CONFIRMED PRESENT and the application as NOT OBSERVED/NOT IDENTIFIED" → "record the principle as CONFIRMED PRESENT and the application as NOT ESTABLISHED (avenue record); the application proposition escalates through the avenue checklist if it matters to a conclusion".
- Add at the top of the Execution section: "**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer."

- [ ] **Step 4: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -nE "NOT OBSERVED|NOT IDENTIFIED|INFERRED|CONTESTED|coverage object" skill-06-conduct-literature-search/SKILL.md || echo "PASS: no legacy states"
grep -n "literature_disclosure" skill-06-conduct-literature-search/SKILL.md
grep -n "avenue" skill-06-conduct-literature-search/SKILL.md
grep -n "Governing principle" skill-06-conduct-literature-search/SKILL.md
```
Expected: no legacy states; literature_disclosure, avenue, governing principle present.

- [ ] **Step 5: Commit**

```bash
git add skill-06-conduct-literature-search/SKILL.md
git commit -m "feat(v1.6): skill-06 — literature_disclosure schema, avenue escalation for negative findings"
```

---

### Task 10: skill-07 analyze-market-opportunity — NAICS, market sizing, adoption, award schemas

**Files:**
- Modify: `skill-07-analyze-market-opportunity/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 registry (`market_relevance_award`, `market_relevance_report`, `market_sizing`, `naics_classification`, `commercial_adoption`), escalation protocol
- Produces: market findings with no guessed classifications, no unsourced figures, no unsupported adoption claims

- [ ] **Step 1: Replace step 1 (market sizing)**

Replace:
"1. Identify primary markets (direct, adjacent, future) with size and CAGR **from cited, defensible sources**. **A quantitative figure that cannot be reconstructed from an identified source must not appear.** If the only available evidence is qualitative (e.g., "AC infrastructure was expanding rapidly in this period"), say that — it is more useful than an impressive-looking number with no reconstructable basis. Mark any derived or estimated figure as INFERRED with its derivation shown."

with:
"1. Identify primary markets (direct, adjacent, future) with size and CAGR using the `market_sizing` schema from GLOSSARY.md: market boundary, geography, time period, figure, source, reconciliation, derivation. **A quantitative figure that cannot be reconstructed from an identified source must not appear** — the proposition fails the Sufficiency Gate and enters the work queue (escalate through the avenue checklist; if exhausted, record in the Operational Audit with `barrier_type: insufficient_identity` or `source_unavailable`). If the only available evidence is qualitative (e.g., "AC infrastructure was expanding rapidly in this period"), say that — it is more useful than an impressive-looking number with no reconstructable basis. Derived figures are analytical inferences, labeled as such, never evidence states."

- [ ] **Step 2: Replace step 2 (NAICS)**

Replace:
"2. Assign a NAICS (or regional equivalent) code."

with:
"2. Assign a NAICS (or regional equivalent) code using the `naics_classification` schema: taxonomy_source (official NAICS/Census documentation), exact code, official title, edition year, and basis (official definition match / activity match / product-manufacturing match). **Never guess a classification.** If the official taxonomy record cannot be established, the classification proposition is excluded from factual findings and recorded in the Operational Audit with `barrier_type: insufficient_identity` — no code is reported."

- [ ] **Step 3: Replace step 6 (technical maturity vs commercial readiness)**

Replace the evidence-state lists and coverage language:
- "Patent disclosure: CONFIRMED PRESENT / NOT OBSERVED / NOT IDENTIFIED" → "Patent disclosure: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)"
- "Prototype evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED" → "Prototype evidence: CONFIRMED PRESENT / CONFIRMED ABSENT / NOT ESTABLISHED (see Operational Audit)"
- Same for Production evidence and Commercial adoption evidence.
- Replace the "No evidence of adoption" bullet: "**"No evidence of adoption" is NOT OBSERVED by default**, not CONFIRMED ABSENT — historical records are rarely dense enough to establish that adoption never occurred. Use CONFIRMED ABSENT only when a **bounded evidence universe** (defined record set with documented completeness and exclusions) is specified and the record is dense enough that absence is meaningful." → "**Adoption is established only through the `commercial_adoption` schema**: a product-identity link (the commercial product is identifiable as embodying the claimed technology), source, date, and ≥2 independent sources (MATERIAL_PROVENANCE_INDEPENDENCE). Absence of adoption evidence is not a finding — the proposition enters the work queue; if avenues are exhausted, it is excluded from factual findings and recorded in the Operational Audit. CONFIRMED ABSENT requires a bounded evidence universe + absence_basis."
- Replace the coverage-object bullet: "**Coverage object on every negative finding.** Every NOT OBSERVED / NOT IDENTIFIED / CONFIRMED ABSENT finding carries a coverage object: scope, temporal scope, source domains (records searched), search depth, completeness (LOW / MEDIUM / HIGH / EXHAUSTIVE), limitations. Coverage is metadata, not evidence — it never changes the evidence state; it only qualifies the reliability of the negative finding and may authorize a targeted re-evaluation. E.g., "commercial adoption of the shield mechanism in US433,700, 1890–1907, source domains: patent records + historical company records + technical literature, completeness: LOW (Westinghouse production records not reviewed)."" → "**Negative findings go through the escalation protocol.** Every unestablished market proposition (adoption, market relevance, market sizing) runs the skill's avenue checklist (A1 primary source search → A2 classification search → A3 citation expansion → A4 terminology expansion → A5 alternate database → A6 organizational records → A7 jurisdiction-specific sources → A8 independent corroboration), logging each avenue_record with the records actually searched (e.g., "commercial adoption of the shield mechanism in US433,700, 1890–1907, avenue records: patent records + historical company records + technical literature; Westinghouse production records BLOCKED — alternate access routes attempted"). EXHAUSTED is not evidence; the proposition is excluded from factual findings."
- "**Commercial readiness:** State "NOT EVALUATED" unless confirmed adoption evidence exists." → "**Commercial readiness:** State "NOT ESTABLISHED" unless adoption evidence passes the Sufficiency Gate; the readiness proposition otherwise enters the work queue."

- [ ] **Step 4: Add market-relevance award schema step and governing principle**

Add after step 1:
"1b. **Market relevance / demand propositions** (e.g., "government procurement activity existed for this technology") use the `market_relevance_award` or `market_relevance_report` schema: agency/publisher, award_id/report_id, recipient, date, title, URL, relevant passage, independence_lineage_id — with ≥2 independent sources. "Various SBIR awards…" with no award identities is not a finding; it is an unestablished proposition that escalates through the avenue checklist."

Add at the top of the Execution section: "**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer."

- [ ] **Step 5: Update the Boundary section**

Replace: "If market data is genuinely insufficient to score actionability, say "NOT IDENTIFIED" rather than filling the gap with plausible-sounding estimates. **Never present an unsourced quantitative claim (revenue, CAGR) as a fact — omit it or mark it INFERRED with derivation.**" → "If market data is genuinely insufficient to score actionability, the proposition is not established: escalate through the avenue checklist; if exhausted, exclude from factual findings and record in the Operational Audit. **Never present an unsourced quantitative claim (revenue, CAGR) as a fact — omit it or record it as an unestablished proposition.**"

- [ ] **Step 6: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -nE "NOT OBSERVED|NOT IDENTIFIED|INFERRED|CONTESTED|coverage object" skill-07-analyze-market-opportunity/SKILL.md || echo "PASS: no legacy states"
grep -n "naics_classification" skill-07-analyze-market-opportunity/SKILL.md
grep -n "commercial_adoption" skill-07-analyze-market-opportunity/SKILL.md
grep -n "market_relevance_award" skill-07-analyze-market-opportunity/SKILL.md
grep -n "Governing principle" skill-07-analyze-market-opportunity/SKILL.md
```
Expected: no legacy states; all four schema references + governing principle present.

- [ ] **Step 7: Commit**

```bash
git add skill-07-analyze-market-opportunity/SKILL.md
git commit -m "feat(v1.6): skill-07 — NAICS/market-sizing/adoption/award schemas, avenue escalation"
```

---

### Task 11: skill-08 identify-partners — partner-fit schema

**Files:**
- Modify: `skill-08-identify-partners/SKILL.md` (root)

**Interfaces:**
- Consumes: Task 1 registry (`partner_fit`), escalation protocol
- Produces: partner candidates with evidenced fit, no exclusivity framing

- [ ] **Step 1: Update step 2 (candidate capture)**

Replace:
"2. For each candidate, capture: organization and website; contact person and role if known; business description; relevance rationale (why *this* invention would interest *this* company specifically, not a generic fit statement); proposed partnership model (licensing, JV, R&D collaboration)."

with:
"2. For each candidate, capture the `partner_fit` schema from GLOSSARY.md: what they sell, what they buy, their technical need, and the mapping to the invention (why *this* invention would interest *this* company specifically, not a generic fit statement) — each field with source_identity. A candidate row without the sell/buy/need/mapping fields does not exist. Also capture: organization and website; contact person and role if known; proposed partnership model (licensing, JV, R&D collaboration)."

- [ ] **Step 2: Update step 4 (counterfactual-exclusivity audit)**

Replace: "Reformulate as "the strongest identified pathway" and explicitly note that alternatives were not identified (NOT OBSERVED) rather than established not to exist." → "Reformulate as "the strongest identified pathway" and explicitly note that alternatives were not established (see Operational Audit) rather than established not to exist."

- [ ] **Step 3: Add governing principle and avenue note**

Add at the top of the Execution section: "**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. A partner-fit proposition that cannot satisfy the `partner_fit` schema escalates through the avenue checklist; if exhausted, it is excluded from factual findings and recorded in the Operational Audit."

- [ ] **Step 4: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "partner_fit" skill-08-identify-partners/SKILL.md
grep -nE "NOT OBSERVED|INFERRED" skill-08-identify-partners/SKILL.md || echo "PASS: no legacy states"
grep -n "Governing principle" skill-08-identify-partners/SKILL.md
```
Expected: partner_fit + governing principle present; no legacy states.

- [ ] **Step 5: Commit**

```bash
git add skill-08-identify-partners/SKILL.md
git commit -m "feat(v1.6): skill-08 — partner-fit schema, no exclusivity framing"
```

---

### Task 12: skill-09 compile-report — three-area report architecture

**Files:**
- Modify: `skill-09-compile-report/SKILL.md` (root)

**Interfaces:**
- Consumes: Tasks 1–11 outputs (finding objects, avenue records, premise maps)
- Produces: the v1.6 report with Established Findings / Analytical Conclusions / Operational Audit

- [ ] **Step 1: Replace the Execution section**

Replace steps 1, 3, 6, 7, 10 with:

"1. Collect all upstream outputs. If any are missing, say so and either invoke the missing skill or explicitly mark the section "NOT ESTABLISHED" in the report — never fill a gap with invented content.
3. Write a 1–2 page executive summary **constrained to Established Findings + Analytical Conclusions** (Executive Summary ⊆ Established Findings + Analytical Conclusions). It may reference the Operational Audit ("Several evidentiary gaps remain and are documented in the Operational Audit") but never convert audit content into factual prose. Label it as a derived executive summary.
6. **Mandatory: Established Findings section.** Only rows that passed the Evidence Sufficiency Gate (CONFIRMED PRESENT / CONFIRMED ABSENT), each rendered from its finding object with full provenance (proposition_id, source_identity, locator, absence_basis where applicable).
7. **Mandatory: Analytical Conclusions section.** Per-gate results whose premises are established findings, each with a premise map (conclusion_id, gate, premises: [proposition_ids], inference: statement + rule_applied, conclusion: assessment). No orphan conclusions; no premise whose status is a work state. **UNRESOLVED may not appear as a terminal analytical conclusion.** Three outcomes only: more work → work layer; all work exhausted → exclude proposition; supported evidence → analytical conclusion permitted.
8. **Mandatory: Operational Audit section.** Every unestablished proposition: proposition_id, work state, avenue dispositions (COMPLETE / BLOCKED / NOT_APPLICABLE + rule_id), barrier_type, remaining_evidentiary_barrier. The reproducible query log = the full escalation ladder (all avenue records, in priority order). **Allowed language:** "Commercial adoption could not be established from the completed evidence protocol." **Prohibited language** (and semantic equivalents) in factual findings: "Not found," "No X was identified," "No evidence of X exists," "appears absent," "there is no evidence that…," "apparently none," "likely not," "could not locate," "no known," "none identified," "no record was found," "Inferred," "Medium completeness.""

Renumber the remaining steps (2 chronology validator, 4 body order, 5 tables, 9 decision matrix, 11 historical status, 12 forward citations, 13 appendices, 14 quality checklist, 15 delivery) accordingly.

- [ ] **Step 2: Replace the quality checklist**

Replace the checklist with:

```markdown
## Quality checklist (all must pass before delivery)
- [ ] Every quantitative claim is sourced — or the proposition is excluded from factual findings and recorded in the Operational Audit. No unsourced revenue or CAGR figures.
- [ ] Chronology validator passed: all dates consistent, no "before [wrong date]" phrasing.
- [ ] Every legal-adjacent statement (patentability, FTO-adjacent, regulatory) carries a "not legal advice" disclaimer.
- [ ] The novelty section explicitly states it is not an FTO opinion if any FTO-adjacent question was raised anywhere in the engagement.
- [ ] The query log (avenue records) is complete enough that a reviewer could re-run any search and reproduce the result set.
- [ ] Every unestablished proposition from upstream skills is carried into the Operational Audit rather than silently dropped.
- [ ] Established Findings contains only CONFIRMED PRESENT / CONFIRMED ABSENT rows, each with full provenance; CONFIRMED ABSENT rows carry absence_basis.
- [ ] Every Analytical Conclusion carries a premise map whose premises are established findings; no premise is a work state.
- [ ] No legacy evidence states (NOT OBSERVED / NOT IDENTIFIED / INFERRED / NOT EVALUATED / CONTESTED / UNRESOLVED) appear as active semantics anywhere in the report.
- [ ] No prohibited negative language ("not found," "no evidence of X exists," "none identified," etc.) appears outside the Operational Audit.
- [ ] Commercial readiness is stated as "NOT ESTABLISHED" unless adoption evidence passes the Sufficiency Gate.
- [ ] Decision matrix output is included, showing the reasoning path, and if obviousness was assessed, the Causal Bridge Test (with bridge_status TRAVERSED/UNTRAVERSED) and the structured obviousness evidence object are provided.
- [ ] Conclusion is multidimensional (per-gate table), not a single compressed patentability label; **no scalar "overall patentability" label appears in the default conclusion output** (an executive score appears only if explicitly requested, labeled as a derived executive summary).
- [ ] Executive Summary ⊆ Established Findings + Analytical Conclusions.
- [ ] No exclusivity framing ("only partner," "no other pathway") survives without an assumption audit.
- [ ] Claim-construction layer (if used) is clearly labeled as "provisional evaluation claim — not a legal claim construction."
```

- [ ] **Step 3: Add governing principle**

Add at the top of the Execution section: "**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer. This skill compiles only — it never converts an unestablished proposition into a factual claim."

- [ ] **Step 4: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "Operational Audit" skill-09-compile-report/SKILL.md
grep -n "premise map" skill-09-compile-report/SKILL.md
grep -nE "NOT OBSERVED|NOT IDENTIFIED|INFERRED|CONTESTED|UNRESOLVED|coverage object" skill-09-compile-report/SKILL.md || echo "PASS: no legacy states"
grep -n "Governing principle" skill-09-compile-report/SKILL.md
```
Expected: Operational Audit + premise map + governing principle present; no legacy states.

- [ ] **Step 5: Commit**

```bash
git add skill-09-compile-report/SKILL.md
git commit -m "feat(v1.6): skill-09 — three-area report architecture, premise maps, operational audit"
```

---

### Task 13: INDEX.md, PIPELINE_STATE.md, README.md — docs

**Files:**
- Modify: `INDEX.md`, `PIPELINE_STATE.md`, `README.md` (root; package copies in Task 14)

**Interfaces:**
- Consumes: Tasks 1–12
- Produces: versioned documentation consistent with v1.6

- [ ] **Step 1: Update INDEX.md**

Replace the "Structural note on this version" section with:

```markdown
## Structural note on this version

**Version: v1.6** — The framework is an evidence-constrained invention reasoning engine built on a **three-layer epistemic architecture** (see GLOSSARY.md): Evidence layer (CONFIRMED PRESENT / CONFIRMED ABSENT only), Work layer (NOT_STARTED / SEARCHING / ESCALATING / REQUIRES VERIFICATION / BLOCKED avenue-level / EXHAUSTED proposition-level), and Analytical layer (evidence → inference → conclusion; inference is never evidence). Every proposition enters the report only through the **Evidence Sufficiency Gate** (schema-driven, atomic, with the proposition-identity firewall). Negative search results are **avenue records** in a deterministic escalation ladder, never evidence. Unestablished propositions are excluded from factual findings and retained in the **Operational Audit** with barrier_type. v1.6 removes the v1.5 negative-evidence states (NOT OBSERVED / NOT IDENTIFIED / INFERRED / NOT EVALUATED / CONTESTED / UNRESOLVED) from active semantics; they survive only in historical reports and the legacy-mapping table. Retained from v1.5: mechanism distance (C0–C4) + design-choice distance (D0–D4, never combined), the Motivation Object, the knowledge decomposition, the Causal Bridge Test (bridge_status TRAVERSED / UNTRAVERSED), and the per-gate-only default conclusion.
```

- [ ] **Step 2: Update PIPELINE_STATE.md**

Append a v1.6 change-log entry (read the existing file first to match its format):

```markdown
## v1.6 (2026-08-14) — Evidence Sufficiency Architecture (breaking change)

- Replaced the 7-state evidence ontology with the three-layer architecture (Evidence / Work / Analytical).
- Added the Evidence Sufficiency Gate as the only admission path for propositions.
- Added the Search Escalation Protocol: fixed per-skill avenue checklists with deterministic priority, avenue_record audit schema, EXHAUSTED as a proposition-level termination state with the invariant that every required avenue is COMPLETE / BLOCKED / NOT_APPLICABLE (none REQUIRES_VERIFICATION).
- Added the Proposition-Schema Registry (single authoritative source; skills reference schema IDs).
- Added the finding object with proposition_id + versioning, source_identity, independence_lineage_id, absence_basis.
- Replaced the Negative Evidence Coverage Rule with the Evidence Sufficiency & Search Escalation Rule.
- Removed UNRESOLVED as a terminal analytical conclusion; removed INFERRED / NOT OBSERVED / NOT IDENTIFIED / NOT EVALUATED / CONTESTED from active semantics.
- Report architecture: Established Findings / Analytical Conclusions (premise maps) / Operational Audit (barrier_type).
- verify.sh: legacy-terminology semantic scan + root/package parity check.
- Validation: Tesla US433,700 v1.6 rerun + negative-control test (see Test-report-results/).
```

- [ ] **Step 3: Update README.md**

Update the version/description line to v1.6 and add one sentence: "v1.6 enforces an evidence-sufficiency architecture: propositions enter the report only through the Evidence Sufficiency Gate, searches escalate through deterministic avenue checklists, and unestablished propositions are excluded from factual findings (see docs/superpowers/specs/2026-08-14-invention-evaluation-framework-v16-design.md)."

- [ ] **Step 4: Verify**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -n "v1.6" INDEX.md PIPELINE_STATE.md README.md
grep -nE "NOT OBSERVED|INFERRED" INDEX.md || echo "PASS: INDEX clean"
```
Expected: v1.6 references in all three; INDEX has no legacy states (except the explicit legacy-mapping mention, which is migration documentation and permitted).

- [ ] **Step 5: Commit**

```bash
git add INDEX.md PIPELINE_STATE.md README.md
git commit -m "docs(v1.6): INDEX, PIPELINE_STATE, README — version and architecture notes"
```

---

### Task 14: Propagation — package mirror, install, parity verification

**Files:**
- Modify: all files under `invention-evaluation-engine/` (mirror of root changes)
- Modify: installed copy at `~/.opencode/skills/invention-evaluation-framework/` (via install.sh)
- Modify: `invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md` (update to v1.6)

**Interfaces:**
- Consumes: Tasks 1–13 root files
- Produces: byte-identical package + installed copy; verify.sh passes parity

- [ ] **Step 1: Mirror root changes into the package**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
for f in GLOSSARY.md DIGEST.md INDEX.md PIPELINE_STATE.md; do cp "$f" "invention-evaluation-engine/docs/$f"; done
for d in skill-01-invention-evaluation-overview skill-02-gather-invention-submission skill-03-analyze-technology-fundamentals skill-04-conduct-patent-landscape skill-05-conduct-novelty-search skill-06-conduct-literature-search skill-07-analyze-market-opportunity skill-08-identify-partners skill-09-compile-report; do cp "$d/SKILL.md" "invention-evaluation-engine/skills/$d/SKILL.md"; done
```

Note: the engine `SKILL.md` lives only in the package (the root holds the nine `skill-XX/` dirs). Task 4 edited `invention-evaluation-engine/SKILL.md` in place; no mirror needed for it. `verify.sh` lives only at root (it is a dev tool that inspects the package); it is not mirrored into the package.

- [ ] **Step 2: Run the verifier — parity must pass**

Run: `cd /home/forsythe/Downloads/invention-evaluation-framework && ./verify.sh`
Expected: ALL CHECKS PASSED (frontmatter, legacy scan clean on all active files, parity root=package for all listed files). If the legacy scan still fails, fix the offending file before continuing.

- [ ] **Step 3: Update the quickstart prompt**

In `invention-evaluation-engine/examples/tesla-us433700/quickstart-prompt.md`, update any v1.5 references to v1.6 and add: "Run under the v1.6 evidence-sufficiency architecture: every proposition passes the Evidence Sufficiency Gate; negative results are avenue records; unestablished propositions go to the Operational Audit."

- [ ] **Step 4: Install to the agent skills directory**

Run: `cd /home/forsythe/Downloads/invention-evaluation-framework && ./install.sh --tool opencode --force`
Expected: package copied to `~/.opencode/skills/invention-evaluation-engine/`.

- [ ] **Step 5: Verify the installed copy**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
for rel in docs/GLOSSARY.md docs/DIGEST.md docs/INDEX.md docs/PIPELINE_STATE.md skills/skill-05-conduct-novelty-search/SKILL.md skills/skill-07-analyze-market-opportunity/SKILL.md skills/skill-09-compile-report/SKILL.md; do
  a=$(sha256sum "invention-evaluation-engine/$rel" | cut -d' ' -f1)
  b=$(sha256sum "$HOME/.opencode/skills/invention-evaluation-engine/$rel" | cut -d' ' -f1)
  [ "$a" = "$b" ] && echo "  [PASS] installed parity: $rel" || echo "  [FAIL] installed parity: $rel"
done
```
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add invention-evaluation-engine/ verify.sh
git commit -m "feat(v1.6): propagate root changes to package; install; parity verified"
```

---

### Task 15: Tesla US433,700 v1.6 rerun + validation matrix + negative-control test

**Files:**
- Create: `Test-report-results/report-tesla-us433700-e2e-v16.md`
- Create: `Test-report-results/validation-matrix-v16.md`
- Create: `Test-report-results/proposition-ledger-v16.md`
- Create: `Test-report-results/avenue-ledger-v16.md`
- Create: `Test-report-results/negative-control-v16.md`
- Create: `invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md` (copy of the report)

**Interfaces:**
- Consumes: Tasks 1–14 (the v1.6 engine), `invention-evaluation-engine/examples/tesla-us433700/submission.md`
- Produces: the validation evidence for all 11 criteria

- [ ] **Step 1: Run the v1.6 pipeline on the Tesla submission**

Execute the nine skills in dependency order (01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09) against `invention-evaluation-engine/examples/tesla-us433700/submission.md`, following each skill's v1.6 rules. Maintain:
- **Proposition Ledger** (`proposition-ledger-v16.md`): every proposition with proposition_id, skill, schema, gate record (required/executed), outcome (ESTABLISHED / EXCLUDED), work_state.
- **Avenue Ledger** (`avenue-ledger-v16.md`): per search proposition, the avenue checklist with priority + status + audit record.

- [ ] **Step 2: Produce the report**

Write `report-tesla-us433700-e2e-v16.md` with the three-area architecture:
1. **Established Findings** — CONFIRMED PRESENT / CONFIRMED ABSENT rows with full provenance (e.g., "US433,700 filed March 26, 1890" with source_identity; prior-art disclosures with patent IDs + relevant passages).
2. **Analytical Conclusions** — per-gate table with premise maps (e.g., obviousness risk with premises = the established prior-art propositions).
3. **Operational Audit** — every unestablished proposition with work state, avenue dispositions, barrier_type, remaining barrier. Expected entries: the 1888–1890 journal full-text access limitation (BLOCKED avenue with alternate routes attempted and logged: Archive.org, Google Books, HathiTrust, periodical indexes); the motivation proposition (work state + avenue ladder); the unexpected-result proposition (`barrier_type: insufficient_technical_demonstration`); market-sizing propositions (`barrier_type: source_unavailable / insufficient_identity`); the commercial-adoption proposition (fails `commercial_adoption` schema → EXCLUDED; report states "Commercial adoption could not be established from the completed evidence protocol" — never "no adoption was identified").

- [ ] **Step 3: Run the negative-control test**

Create `negative-control-v16.md`. Inject these malformed propositions into the v1.6 admission pipeline (the Sufficiency Gate + escalation logic as defined in GLOSSARY.md and skill-07):

```text
1. "Various SBIR awards for spray cooling in military applications" → confirms market relevance
2. "NAICS 334419 – inferred"
3. "Research on spray cooling for UAVs and military applications"
4. "No international equivalents found."
5. "Commercial adoption not observed."
```

For each: run the gate. Expected: ALL FAIL the Sufficiency Gate (missing required schema fields: award_id / taxonomy_source / publication identity / bounded universe / product-identity link) → SEARCH ESCALATION or EXHAUSTED → EXCLUDED. **None may become a finding.** Document each rejection with the failing schema field.

- [ ] **Step 4: Build the Validation Matrix**

Create `validation-matrix-v16.md`:

| # | Criterion | Expected invariant | Evidence location | Automated check | Result |
|---|---|---|---|---|---|
| 1 | Evidence Sufficiency Gate exercised on every proposition | Every proposition has a gate record | Proposition Ledger | Count equality: total propositions = propositions with gate record | |
| 2 | Mandatory search-escalation loop exercised | Every required avenue dispositioned, order preserved, audit record present | Avenue Ledger | Required-state check + priority order check | |
| 3 | Correct state-level placement | BLOCKED avenue-level; EXHAUSTED proposition-level | Audit records | Schema validation: fail on proposition.work_state: BLOCKED or avenue.status: EXHAUSTED | |
| 4 | No legacy evidence states | No legacy state in active finding objects | Report + active files | Anti-pattern scan (verify.sh) | |
| 5 | Source-level provenance on every substantive assertion | Factual assertions have source_identity + locator; conclusions have premise maps | Findings + conclusions | Schema validator | |
| 6 | Proposition-identity matching | IDs + versions stable across hand-offs; no silent re-scope | Hand-off artifacts | ID/version comparison | |
| 7 | No guessed content | No INFERRED/ASSUMED/LIKELY/PROBABLY/ESTIMATED in audit objects without source support / inference object / escalation / exclusion | Audit objects | Scan | |
| 8 | Evidence vs. inference separated | Every conclusion has a premise map; no premise is a work state | Analytical Conclusions | Structural premise-map validation | |
| 9 | No unsupported UNRESOLVED terminal | UNRESOLVED absent as terminal conclusion | Report | Scan | |
| 10 | Hard stopping only on established evidence or genuine exhaustion | Only two valid stops | Avenue Ledger + report | Stop-mode audit | |
| 11 | Negative-control test | All 5 injected propositions fail the gate → EXCLUDED | negative-control-v16.md | Admission-pipeline run | |

Fill the Result column with PASS/FAIL for each criterion.

- [ ] **Step 5: Verify the report against the prohibited-language rule**

Run:
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
grep -nE "not found|no evidence of|none identified|no record was found|could not locate|appears absent|apparently none|likely not|no known" Test-report-results/report-tesla-us433700-e2e-v16.md | grep -v "Operational Audit" || echo "PASS: no prohibited negative language outside Operational Audit"
grep -nE "INFERRED|UNRESOLVED|NOT OBSERVED|NOT IDENTIFIED|CONTESTED" Test-report-results/report-tesla-us433700-e2e-v16.md || echo "PASS: no legacy states in report"
```
Expected: PASS lines (any matches must be confined to the Operational Audit section).

- [ ] **Step 6: Copy the report into the package examples**

Run: `cp Test-report-results/report-tesla-us433700-e2e-v16.md invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md`

- [ ] **Step 7: Final full verification**

Add the v1.6 example report to verify.sh's existence checks (it now exists):
```bash
cd /home/forsythe/Downloads/invention-evaluation-framework
# insert after the quickstart-prompt check line in verify.sh:
#   check "example report v1.6" "$TARGET/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md"
```
Then run: `./verify.sh`
Expected: ALL CHECKS PASSED.

- [ ] **Step 8: Commit**

```bash
git add Test-report-results/ invention-evaluation-engine/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md verify.sh
git commit -m "test(v1.6): Tesla US433,700 rerun — report, ledgers, validation matrix, negative-control test"
```

---

## Self-Review Notes

**Spec coverage check:**
- Section 1 (epistemic architecture) → Task 1 (GLOSSARY), Task 3 (DIGEST), Task 4 (skills 01/engine)
- Section 2 (Sufficiency Gate) → Task 1, Tasks 6–12 (skills emit into the gate)
- Section 3 (escalation protocol) → Task 1, Tasks 7–10 (avenue checklists in skills 04/05/06/07)
- Section 4 (finding object + identity) → Task 1, Tasks 4/6/10/11 (proposition_id, schemas)
- Section 5 (report architecture) → Task 12 (skill-09), Task 15 (report)
- Section 6 (change map + propagation + verify.sh + git) → Tasks 2, 13, 14
- Section 7 (validation: 11 criteria, ledgers, matrix, negative control) → Task 15
- Five final edits (EXHAUSTED invariant, lineage IDs, provenance by layer, schema registry, CONFIRMED ABSENT rule) → Task 1 (all five in GLOSSARY), Task 12 (provenance by layer in skill-09)

**Placeholder scan:** No TBD/TODO; every step contains concrete content or exact commands.

**Type consistency:** `proposition_id` / `proposition_version` / `source_identity` / `independence_lineage_id` / `absence_basis` / `barrier_type` / `avenue_record` / `search_escalation` / `bridge_work_state` / `motivation_work_state` are defined once in Task 1 and used identically in Tasks 4–15. Schema IDs (`prior_art_disclosure`, `literature_disclosure`, `market_relevance_award`, `market_relevance_report`, `market_sizing`, `naics_classification`, `commercial_adoption`, `regulatory_regime`, `partner_fit`, `performance_data`) are defined in Task 1's registry and referenced identically in Tasks 6–11.