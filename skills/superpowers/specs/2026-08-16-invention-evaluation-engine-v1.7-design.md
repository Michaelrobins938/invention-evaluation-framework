# Invention Evaluation Engine v1.7 — Inference Architecture Upgrade

**Status:** Design approved by user; implementation not started.  
**Baseline:** v1.6 US8527057 evaluation artifacts and report.  
**Scope:** Reasoning control layer between evidence collection and conclusion generation.

## 1. Purpose

v1.6 provides an Evidence Sufficiency Architecture: it preserves provenance, avoids
unsupported claims, records evidence states, and renders audit artifacts. v1.7 adds an
Evidence Recovery Architecture. Its job is to prevent uncertainty from becoming an
unexamined stopping point.

The engine must distinguish:

```text
Evidence missing because no recovery was attempted
Evidence missing after required recovery paths were attempted
Evidence unavailable because it is proprietary, legally restricted, or genuinely absent
```

The PDF remains a presentation layer. Reasoning state, constraints, and recovery work
must live in machine-readable engine artifacts first.

## 2. Architectural principle

> No conclusion may be stronger than the weakest unresolved dependency that materially
> supports it.

The engine is a graph, not only a linear report pipeline:

```text
Sources
  ↓
Evidence normalizer
  ├── Claim graph
  ├── Asset/family graph
  ├── Prior-art engine
  └── Rights/status engine
          ↓
Inference and bridge engine
          ↓
Asset/value and decision engine
          ↓
Presentation compiler
```

## 3. Evidence Recovery Controller

The controller is a reusable service invoked whenever any phase creates an unresolved
proposition. It is not a linear Phase 0.5 and does not run only once.

### 3.1 Controller workflow

```text
Unknown detected
  ↓
Missingness classifier
  ↓
Evidence-leverage calculation
  ↓
Recovery policy selection
  ↓
Escalation ladder execution
  ↓
Evidence graph update
  ↓
Constraint propagation
  ↓
Resolution, escalation-required, or search-exhausted state
```

### 3.2 Missingness taxonomy

```yaml
unknown_type:
  - not_searched
  - insufficient_query
  - unavailable_source
  - ambiguous_identity
  - missing_primary_record
  - proprietary_information
  - legally_sensitive
  - contradictory_sources
  - search_exhausted
```

Required responses:

- `not_searched`: execute the minimum recovery path.
- `insufficient_query`: reformulate, broaden, narrow, or switch terminology.
- `unavailable_source`: use an alternate primary/secondary source or bounded proxy.
- `ambiguous_identity`: resolve patent, company, product, or family identity.
- `proprietary_information`: identify proxy evidence and label decision value.
- `legally_sensitive`: preserve the limitation and escalate to counsel where required.
- `contradictory_sources`: open a contradiction record; do not average the sources.
- `search_exhausted`: only valid after the exhaustion proof passes.

### 3.3 State replacement

The broad `EXHAUSTED` state is removed from active reasoning.

```text
ESCALATION_REQUIRED
  Another required evidence path remains unattempted.

SEARCH_EXHAUSTED
  Required investigation paths were attempted and no sufficient evidence was found.

BLOCKED
  Execution cannot continue without a credential, permission, source, or user input.
```

Historical v1.6 `EXHAUSTED` values remain readable as migration data but cannot satisfy
a v1.7 completion gate without a mapped disposition.

## 4. Research exhaustion proof

Every unresolved high-impact proposition must carry an exhaustion record.

```yaml
research_exhaustion:
  proposition_id: P-05-001
  attempted:
    sources:
      - Google Patents
      - USPTO
      - Espacenet
    methods:
      - keyword
      - verified classification
      - citation traversal
      - family traversal
      - prosecution-history review
      - forward-citation review
    coverage:
      claim_domains_checked: 2
      claims_checked: [1]
      limitations_checked: 7
      critical_date: 2005-04-28
  results:
    qualifying_references: 0
    partial_references: 4
    rejected_references: 3
  remaining_uncertainty:
    - unavailable proprietary examiner reasoning
  disposition: SEARCH_EXHAUSTED
```

The engine must reject `SEARCH_EXHAUSTED` when the required source, method, or coverage
fields are missing.

## 5. Evidence leverage

Each proposition receives a leverage score based on how many downstream conclusions it
can materially change.

```yaml
evidence_leverage:
  proposition_id: P-05-001
  importance: critical
  affected_nodes:
    - anticipation
    - patentability_confidence
    - ip_leverage
    - investor_recommendation
  resolution_value: high
  recovery_priority: 1
```

Recovery priority is determined by impact × uncertainty × reversibility of downstream
decisions. Low-leverage unknowns may remain queued while high-leverage blockers are
resolved first.

## 6. Claim Intelligence Engine

Claim construction becomes a first-class graph.

```yaml
claim_graph:
  claim_id: US8527057-claim-1
  domains:
    - name: retinal_interface
      limitations: [L1]
    - name: mechanical_fixation
      limitations: [L2]
    - name: electronics
      limitations: [L3]
    - name: interconnect
      limitations: [L4]
    - name: power_architecture
      limitations: [L5a, L5b, L5c, L5d]
  relationships:
    - [L2, constrains, L5b]
    - [L3, powered_by, L5d]
    - [L4, connects, L1]
  inventive_center_candidates:
    - cross-domain spatial integration
    - low-profile scleral geometry
```

The engine must generate separate vectors for:

1. Product/architecture claims.
2. Packaging/material claims.
3. Manufacturing/process claims.
4. Dependent and surgical-handling features.

Each vector receives independent prior-art, technical-value, competitive, and asset-value
analysis.

## 7. Prior-Art Engine

Minimum escalation when continuity, same-assignee art, or close product lineage is found:

1. Claim limitation decomposition.
2. Critical-date qualification.
3. Patent-family tree.
4. Parent, continuation, divisional, and foreign-counterpart review.
5. Applicant and examiner citations.
6. Forward-citation review.
7. Prosecution-history review where available.
8. Limitation-by-reference matrix.
9. Anticipation determination.
10. Combination/obviousness bridge analysis.

Required output states:

```text
ANTICIPATION: ESTABLISHED
ANTICIPATION: NOT ESTABLISHED AFTER COMPLETE SEARCH
ANTICIPATION: UNRESOLVED — SEARCH-INCOMPLETE
```

The third state must not be presented visually as a positive novelty conclusion.

## 8. Rights and Asset Engine

Legal status is upstream infrastructure, not an optional report section.

```yaml
rights_graph:
  patent: US8527057B2
  family:
    priority: US60675980
    parent: US7881799B2
    divisionals: []
    continuations: []
    foreign_counterparts: []
  status:
    jurisdiction: US
    active: false
    state: EXPIRED
    reason: maintenance_fee_nonpayment
    effective_lapse_date: 2025-09-03
    public_record_date: 2025-10-06
  assignments:
    - assignee: Vivani Medical
      date: 2022
    - assignee: Cortigent
      date: 2023
  asset_layers:
    - surviving_family_rights
    - know_how
    - regulatory_assets
    - clinical_data
    - historical_technology
```

If standalone enforcement leverage is false, the engine must block an unqualified
`patent licensing` recommendation and activate portfolio/know-how/family analysis.

## 9. Commercial and lifecycle analysis

Commercial analysis must not stop at missing TAM. It must distinguish:

- patient population and clinical eligibility;
- addressable candidates;
- device/procedure economics;
- reimbursement and adoption barriers;
- comparable products;
- commercialization history;
- regulatory pathway;
- failure or success mode.

Every mature biomedical technology receives a lifecycle classification:

```text
technical_failure
regulatory_failure
reimbursement_failure
market_failure
timing_failure
business_model_failure
undetermined
```

The engine must also run a technology-resurrection analysis: whether changed
manufacturing, AI, batteries, regulatory pathways, or clinical practice could create
future value despite historical commercialization failure.

## 10. Landscape normalization

Landscape outputs are separated into three layers:

```text
Retrieval
  Raw search-return publication records.

Normalization
  Deduplication, family grouping, assignee normalization, dates, status, relevance.

Inference
  Competitive density, clusters, trajectory, active rights, claim overlap.
```

Raw retrieval counts must never be labeled as meaningful competitive assets without a
normalization state and relevance type.

Evidence objects carry:

```yaml
relevance:
  direct: false
  adjacent: true
  contextual: true
  decision_value: low
```

## 11. Constraint propagation

The decision engine must propagate upstream constraints automatically.

Examples:

```text
Prior-art search incomplete
  → anticipation unresolved
  → patentability confidence capped
  → IP leverage capped
  → commercial confidence capped
```

```text
Patent expired
  → standalone enforcement leverage minimized
  → patent-license recommendation blocked
  → family/know-how/regulatory analysis activated
```

No downstream node may silently upgrade a constrained dependency.

## 12. Internal assessment vectors

The engine retains vectors; presentation gauges are derived views only.

```yaml
assessment:
  technical:
    distinctiveness: null
    integration_complexity: null
    evidence_confidence: null
  ip:
    claim_specificity: null
    prior_art_separation: null
    search_completeness: null
    legal_leverage: null
    family_leverage: null
  commercial:
    market_need: null
    commercialization_readiness: null
    partnerability: null
    evidence_confidence: null
```

Missing values remain missing. The presentation compiler may derive a tier only when the
vector and confidence cap rules permit it.

## 13. Regression requirements

US8527057 v1.6 is the diagnostic specimen and regression baseline. A v1.7 rerun must
demonstrate:

- legal-status verification before commercial scoring;
- family and assignment graph construction;
- product/process claim-domain separation;
- complete required prior-art escalation or explicit `ESCALATION_REQUIRED` state;
- `PARTIALLY_TRAVERSED` bridge vector rather than binary `TRAVERSED`;
- product, clinical, regulatory, and commercialization breadcrumb following;
- lifecycle/failure/resurrection analysis;
- retrieval/normalization/inference separation;
- evidence leverage and evidence debt;
- downstream score and recommendation constraints;
- report and companion generated from the graph;
- v1.6 artifacts preserved as regression fixtures.

## 14. Non-goals

- This version does not provide legal advice or replace counsel.
- This version does not fabricate proprietary market or prosecution data.
- This version does not require every unknown to become resolved.
- This version does not make the PDF the system of record.
- This version does not silently rewrite historical v1.6 results.

## 15. Acceptance criterion

The upgrade is successful only if the engine converts avoidable unknowns into executed
recovery attempts, preserves genuine uncertainty with proof of exhaustion, and prevents
that uncertainty from being washed out by downstream scores or recommendations.

The primary acceptance question is:

> Did the engine systematically convert avoidable unknowns into resolved evidence while
> preserving uncertainty where evidence truly does not exist?
