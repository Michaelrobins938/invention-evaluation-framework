# Invention Evaluation Engine v1.7 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an evidence-recovery control layer that mechanically constrains downstream invention conclusions, while preserving v1.6 report behavior as a regression baseline.

**Architecture:** Introduce small Python standard-library modules for propositions, recovery policies, claim graphs, rights/assets, inference constraints, and evidence debt. Keep the existing phase skills as declarative policy inputs; make the renderer consume compiled graph artifacts rather than inventing reasoning. Rerun US8527057 from its submission record through v1.7 compilation and rendering.

**Tech Stack:** Python 3, JSON/YAML-like Markdown artifacts, existing Markdown renderer, Chromium PDF generation, shell verification in `verify.sh`, pytest for new unit/integration tests.

## Global Constraints

- No conclusion may be stronger than the weakest unresolved dependency that materially supports it.
- `NOT_ESTABLISHED` is not a terminal state until a research exhaustion proof passes.
- Active reasoning may use `ESCALATION_REQUIRED`, `SEARCH_EXHAUSTED`, and `BLOCKED`; v1.6 `EXHAUSTED` is migration-only.
- Legal status is upstream infrastructure and must precede commercial leverage or partner recommendations.
- The PDF is a presentation layer; the evidence graph and recovery records are the system of record.
- No proprietary, legal, clinical, market, or patent facts may be fabricated to satisfy a chart or score.
- Do not change or overwrite the v1.6 US8527057 artifacts; write v1.7 outputs beside them.
- Do not create a git commit unless explicitly requested by the user.

---

## File map

Create the v1.7 control layer under `invention-evaluation-engine/engine_v17/`:

- `models.py` — typed dataclasses and serialization for propositions, sources, recovery attempts, claim graphs, rights graphs, assessments, and evidence debt.
- `recovery.py` — missingness classification, leverage scoring, policy selection, exhaustion validation, and state transitions.
- `claim_graph.py` — claim-domain decomposition and product/process vector generation.
- `rights_graph.py` — family, assignment, status, maintenance, and asset-layer normalization.
- `constraints.py` — dependency graph and downstream confidence/recommendation caps.
- `landscape.py` — retrieval/normalization/inference separation and relevance typing.
- `compiler.py` — compile graph artifacts into report-facing JSON/Markdown inputs.
- `migration.py` — map v1.6 artifacts into v1.7 states without treating legacy `EXHAUSTED` as proven exhaustion.

Create tests under `invention-evaluation-engine/tests_v17/`:

- `test_recovery.py`
- `test_claim_graph.py`
- `test_rights_graph.py`
- `test_constraints.py`
- `test_landscape.py`
- `test_migration.py`
- `test_us8527057_acceptance.py`

Modify:

- `invention-evaluation-engine/SKILL.md` — v1.7 orchestration contract.
- `invention-evaluation-engine/skills/skill-04-conduct-patent-landscape/SKILL.md` — escalation policy and retrieval/normalization/inference stages.
- `invention-evaluation-engine/skills/skill-05-conduct-novelty-search/SKILL.md` — claim-aware escalation and explicit anticipation states.
- `invention-evaluation-engine/skills/skill-07-analyze-market-opportunity/SKILL.md` — bounded commercial/lifecycle recovery.
- `invention-evaluation-engine/skills/skill-08-identify-partners/SKILL.md` — rights-state constraints and asset-layer recommendations.
- `invention-evaluation-engine/skills/skill-09-compile-report/SKILL.md` — graph-derived conclusion rules.
- `invention-evaluation-engine/skills/skill-10-render-report/SKILL.md` — render graph constraints and evidence debt.
- `invention-evaluation-engine/report-renderer/render_report.py` — consume v1.7 compiled inputs and reject unsupported legacy fallbacks.
- `invention-evaluation-engine/report-renderer/template.html` — show confidence, blockers, evidence debt, and next recovery action.
- `verify.sh` — parity checks, schema checks, and v1.7 semantic invariants.

Create v1.7 regression artifacts under `evaluations/us8527057-v17/` without modifying `evaluations/us8527057/`.

---

## Task 1: Add graph models and schema validation

**Files:**
- Create: `invention-evaluation-engine/engine_v17/models.py`
- Create: `invention-evaluation-engine/tests_v17/test_recovery.py`

**Interfaces:**
- `Proposition.from_dict(data: dict) -> Proposition`
- `Proposition.to_dict() -> dict`
- `ResearchExhaustion.validate() -> list[str]`
- `EvidenceLeverage.to_dict() -> dict`
- `UnknownType`, `ResolutionState`, and `EvidenceState` enums.

- [ ] **Step 1: Write failing model tests**

```python
def test_exhaustion_requires_sources_methods_and_coverage():
    record = ResearchExhaustion.from_dict({"proposition_id": "P-05-001"})
    assert "attempted.sources" in record.validate()
    assert "attempted.methods" in record.validate()
    assert "attempted.coverage" in record.validate()

def test_legacy_exhausted_is_not_active_v17_state():
    proposition = Proposition.from_dict({"id": "P-07-001", "state": "EXHAUSTED"})
    assert proposition.state == ResolutionState.MIGRATION_REQUIRED
```

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_recovery.py -q`  
Expected: FAIL because the v1.7 model classes do not exist.

- [ ] **Step 3: Implement dataclasses and strict validation**

Use `dataclasses`, `enum`, and `typing`; reject unknown active states and preserve raw
legacy values under `migration_metadata`.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_recovery.py -q`  
Expected: PASS.

## Task 2: Implement the Evidence Recovery Controller

**Files:**
- Create: `invention-evaluation-engine/engine_v17/recovery.py`
- Modify: `invention-evaluation-engine/tests_v17/test_recovery.py`

**Interfaces:**
- `classify_missingness(proposition: Proposition) -> UnknownType`
- `score_evidence_leverage(proposition: Proposition, graph: EvidenceGraph) -> EvidenceLeverage`
- `select_recovery_policy(proposition: Proposition) -> RecoveryPolicy`
- `transition_state(proposition: Proposition, attempts: list[RecoveryAttempt]) -> ResolutionState`
- `validate_search_exhaustion(proposition: Proposition) -> list[str]`

- [ ] **Step 1: Add failing tests for state transitions**

Cover `NOT_SEARCHED → ESCALATION_REQUIRED`, blocked source → `BLOCKED`, complete
required attempts with no result → `SEARCH_EXHAUSTED`, and unresolved high-impact
propositions receiving a confidence cap.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_recovery.py -q`  
Expected: FAIL on missing controller functions.

- [ ] **Step 3: Implement controller and recovery policies**

Implement policy ladders for patent, status, market, literature, commercialization,
and partner propositions. Require query, source, result count, rejection reason, and
coverage for every terminal `SEARCH_EXHAUSTED` transition.

- [ ] **Step 4: Add leverage-priority ordering test**

Verify a critical anticipation blocker sorts before a low-impact partner contact gap.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_recovery.py -q`  
Expected: PASS.

## Task 3: Implement claim-domain decomposition

**Files:**
- Create: `invention-evaluation-engine/engine_v17/claim_graph.py`
- Create: `invention-evaluation-engine/tests_v17/test_claim_graph.py`

**Interfaces:**
- `decompose_claim(claim: dict) -> ClaimGraph`
- `derive_claim_vectors(graph: ClaimGraph) -> list[ClaimVector]`
- `find_inventive_center(graph: ClaimGraph) -> list[str]`

- [ ] **Step 1: Write US8527057 claim fixture tests**

Assert separate vectors for retinal interface, fixation, electronics/packaging,
interconnect, power architecture, manufacturing, and dependent handling features.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_claim_graph.py -q`  
Expected: FAIL because decomposition is not implemented.

- [ ] **Step 3: Implement domain graph and relationship extraction**

Preserve limitation IDs, claim text, dependencies, spatial relationships, and product
versus process classification. Inventive-center candidates must be hypotheses, not facts.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_claim_graph.py -q`  
Expected: PASS.

## Task 4: Implement rights and family asset graph

**Files:**
- Create: `invention-evaluation-engine/engine_v17/rights_graph.py`
- Create: `invention-evaluation-engine/tests_v17/test_rights_graph.py`

**Interfaces:**
- `build_rights_graph(records: list[dict]) -> RightsGraph`
- `legal_leverage(graph: RightsGraph) -> LegalLeverage`
- `recommendation_constraints(graph: RightsGraph) -> list[Constraint]`

- [ ] **Step 1: Write status-gate tests**

Use US8527057 fixtures to assert maintenance-fee lapse produces `active=False`,
`legal_leverage="minimal"`, and blocks standalone patent licensing.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_rights_graph.py -q`  
Expected: FAIL because the rights graph does not exist.

- [ ] **Step 3: Implement family, assignment, status, and asset-layer handling**

Support parent/divisional/continuation/foreign edges, assignment events, maintenance
events, expiration/lapse reasons, reinstatement state, surviving rights, know-how,
clinical data, regulatory assets, and historical technology.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_rights_graph.py -q`  
Expected: PASS.

## Task 5: Implement constraint propagation and evidence debt

**Files:**
- Create: `invention-evaluation-engine/engine_v17/constraints.py`
- Create: `invention-evaluation-engine/tests_v17/test_constraints.py`

**Interfaces:**
- `build_dependency_graph(propositions: list[Proposition]) -> DependencyGraph`
- `propagate_constraints(graph: DependencyGraph) -> list[Constraint]`
- `calculate_evidence_debt(graph: DependencyGraph) -> list[EvidenceDebtItem]`
- `cap_assessment(assessment: Assessment, constraints: list[Constraint]) -> Assessment`

- [ ] **Step 1: Write failing propagation tests**

Verify incomplete anticipation caps patentability/IP confidence; expired patent blocks
standalone licensing; unresolved market evidence caps commercial confidence; and all
constraints appear in the compiled output.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_constraints.py -q`  
Expected: FAIL because propagation is not implemented.

- [ ] **Step 3: Implement graph propagation and evidence debt ranking**

Use criticality, uncertainty, affected-node count, and recovery priority. Never average
away a hard blocker.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_constraints.py -q`  
Expected: PASS.

## Task 6: Separate landscape retrieval, normalization, and inference

**Files:**
- Create: `invention-evaluation-engine/engine_v17/landscape.py`
- Create: `invention-evaluation-engine/tests_v17/test_landscape.py`

**Interfaces:**
- `record_retrieval(records: list[dict], query: QueryRecord) -> RetrievalSet`
- `normalize_landscape(retrieval: RetrievalSet) -> NormalizedLandscape`
- `infer_landscape(landscape: NormalizedLandscape) -> LandscapeInference`

- [ ] **Step 1: Write tests showing raw counts cannot become competitive conclusions**

Assert that publication count is labeled retrieval volume until family grouping,
assignee normalization, status filtering, and relevance typing are complete.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_landscape.py -q`  
Expected: FAIL because the three-layer API does not exist.

- [ ] **Step 3: Implement retrieval, normalization, relevance, and inference types**

Include direct/adjacent/contextual relevance and decision value. Preserve query/source
metadata and prevent unrelated classification data from entering inference.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_landscape.py -q`  
Expected: PASS.

## Task 7: Add v1.7 compiler and migrate the declarative skill contracts

**Files:**
- Create: `invention-evaluation-engine/engine_v17/compiler.py`
- Create: `invention-evaluation-engine/engine_v17/migration.py`
- Modify: `invention-evaluation-engine/SKILL.md`
- Modify: `skills/skill-04-conduct-patent-landscape/SKILL.md`
- Modify: `skills/skill-05-conduct-novelty-search/SKILL.md`
- Modify: `skills/skill-07-analyze-market-opportunity/SKILL.md`
- Modify: `skills/skill-08-identify-partners/SKILL.md`
- Modify: `skills/skill-09-compile-report/SKILL.md`
- Modify: `skills/skill-10-render-report/SKILL.md`
- Create: `invention-evaluation-engine/tests_v17/test_migration.py`

**Interfaces:**
- `compile_v17_artifacts(graph: EvidenceGraph, out_dir: Path) -> CompiledArtifacts`
- `migrate_v16_artifact(data: dict) -> Proposition`
- `validate_v17_completion(artifacts: CompiledArtifacts) -> list[str]`

- [ ] **Step 1: Write migration tests**

Assert v1.6 `EXHAUSTED` maps to `MIGRATION_REQUIRED`, not `SEARCH_EXHAUSTED`, unless
an exhaustion proof is attached.

- [ ] **Step 2: Implement compiler and migration**

Emit `evidence-graph.json`, `claim-graph.json`, `rights-graph.json`,
`constraint-report.json`, `evidence-debt.json`, and report-facing score inputs.

- [ ] **Step 3: Update skill contracts**

Add mandatory evidence recovery, minimum depth, breadcrumb, status-gate, and
downstream-constraint rules. Keep root/package copies byte-identical.

- [ ] **Step 4: Run tests and parity checks**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_migration.py -q`  
Run: `./verify.sh`  
Expected: focused tests PASS and root/package parity PASS.

## Task 8: Update the presentation compiler and renderer

**Files:**
- Modify: `invention-evaluation-engine/report-renderer/render_report.py`
- Modify: `invention-evaluation-engine/report-renderer/template.html`
- Add renderer tests to `invention-evaluation-engine/tests_v17/test_constraints.py`

**Interfaces:**
- Renderer input: `CompiledArtifacts`, not raw scores alone.
- Every gauge block: value, confidence, basis IDs, blockers, evidence debt, next recovery action.

- [ ] **Step 1: Add renderer assertions**

Require visible status state, confidence, blocker, and next-evidence fields for any
constrained score. Reject hard-coded domain-specific fallback numbers and mismatched
classification codes.

- [ ] **Step 2: Implement graph-driven presentation blocks**

Keep charts and typography from v1.6, but populate all reasoning text from compiled
artifacts. Use placeholders only when the graph says `SEARCH_EXHAUSTED` or `BLOCKED`.

- [ ] **Step 3: Render fixture and run PDF checks**

Run: `python3 invention-evaluation-engine/report-renderer/render_report.py ... --pdf`  
Run: `pdfinfo ...` and `pdftotext ...` checks for A4, page counters, TOCMARK absence,
visible blockers, visible status, and no wrong-industry tokens.

## Task 9: Rerun US8527057 as the v1.7 acceptance case

**Files:**
- Create: `evaluations/us8527057-v17/submission-us8527057.md`
- Create: `evaluations/us8527057-v17/evidence-graph.json`
- Create: `evaluations/us8527057-v17/claim-graph.json`
- Create: `evaluations/us8527057-v17/rights-graph.json`
- Create: `evaluations/us8527057-v17/constraint-report.json`
- Create: `evaluations/us8527057-v17/evidence-debt.json`
- Create: `evaluations/us8527057-v17/report-us8527057-v17.md`
- Create: `evaluations/us8527057-v17/report-us8527057-v17.html`
- Create: `evaluations/us8527057-v17/report-us8527057-v17.pdf`
- Create: `invention-evaluation-engine/tests_v17/test_us8527057_acceptance.py`

- [ ] **Step 1: Write acceptance assertions**

Require:

```python
assert rights.status == "EXPIRED"
assert rights.legal_leverage == "MINIMAL"
assert recommendation.primary_strategy != "patent licensing"
assert anticipation.status == "UNRESOLVED — SEARCH-INCOMPLETE"
assert bridge.state == "PARTIALLY_TRAVERSED"
assert evidence_debt.high_impact_count > 0
assert any(item.unknown_type == "search_exhausted" for item in evidence_debt.items)
```

- [ ] **Step 2: Run the acceptance test before implementation is considered complete**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17/test_us8527057_acceptance.py -q`  
Expected: PASS only when v1.7 graph artifacts and rendered report satisfy all assertions.

- [ ] **Step 3: Perform targeted visual inspection**

Rasterize the cover, executive/status page, claim analysis page, landscape pages,
commercial/partner pages, and final appendix pages. Record inspected page numbers in
the acceptance artifact; do not claim full visual inspection unless every page was opened.

## Task 10: Final verification and handoff

**Files:**
- Modify: `verify.sh`
- Modify: `invention-evaluation-engine/docs/PIPELINE_STATE.md`
- Modify: `invention-evaluation-engine/docs/DIGEST.md`
- Modify: `invention-evaluation-engine/docs/GLOSSARY.md`

- [ ] **Step 1: Add v1.7 invariant checks**

Check schema validity, root/package parity, forbidden legacy active states, status-gate
presence, exhaustion-proof presence, classification consistency, and renderer artifacts.

- [ ] **Step 2: Run the complete verification suite**

Run: `./verify.sh`  
Expected: ALL CHECKS PASSED.

- [ ] **Step 3: Run the complete v1.7 acceptance suite**

Run: `python3 -m pytest invention-evaluation-engine/tests_v17 -q`  
Expected: all unit, migration, renderer, and US8527057 acceptance tests pass.

- [ ] **Step 4: Record evidence and remaining gaps**

Write the actual commands, outputs, inspected page numbers, unresolved propositions,
and recovery queues into the v1.7 run manifest. Do not describe targeted inspection as
full visual inspection.

---

## Self-review

- **Spec coverage:** All v1.7 design sections map to Tasks 1–10: controller, exhaustion
  proof, leverage, states, claim graph, rights graph, lifecycle analysis, landscape
  normalization, constraints, vectors, evidence debt, renderer, and regression case.
- **Placeholder scan:** No unfinished or unspecified implementation step remains.
- **Type consistency:** Interfaces use `Proposition`, `ResearchExhaustion`, `EvidenceGraph`,
  `ClaimGraph`, `RightsGraph`, `DependencyGraph`, `CompiledArtifacts`, and `Assessment`
  consistently across tasks.
- **Scope:** The work is decomposed into independently testable engine units, followed by
  compiler/renderer integration and one acceptance rerun.
