# Architecture — Invention Evaluation Framework

Detailed execution model for `README.md` (product overview). This document is the technical authority for the current implementation (`engine_v17` + `autoprompt` + `schemas` + `report-renderer`).

## 1. Execution Model

```
USER REQUEST
    │
    ▼
AUTOPROMPT L0 CONDUCTOR
  mission hash (sha256) + RUN-NONCE in PROMPTS.txt
    │
    ▼
IEF MISSION ADAPTER  engine_v17/autoprompt_adapter.py
  adapt_autoprompt_mission_to_ief → EvaluationMission
  build_execution_plan → ExecutionPlan (DAG slice + launch groups)
    │
    ▼
IEF DOMAIN ORCHESTRATOR  skills/SKILL-Orchestrator.md
  skill selection via schemas/skill_registry.json
  validates hard/soft deps, emits mission+plan
    │
    ▼
AUTOPROMPT L1 COORDINATORS
  ap-scope-coordinator (scope, 3 agents/2 rounds bounded)
  ap-feature-coordinator (feature lanes)
  ap-sweep-coordinator (convergence)
    │
    ├── L2 ap-manager (multi-track, optional)
    │
    ▼
L3 EXECUTORS  engine_v17/workers.py
  ap-scribe, ap-scoper, ap-researcher, ap-synthesizer
  one per DAG node, spawn-all-then-collect per launch group
    │
    ▼
L4 LEAVES
  ap-reviewer (independent), ap-fresh-verifier (blind), ap-arbiter
    │
    ▼
EVIDENCE CONTROLLER  engine_v17/evidence_gate.py + epistemic_gates.py + coverage.py
  Sufficiency Gate, avenue checklists, coverage gates, E0-E9
    │
    ▼
EVIDENCE / PROPOSITION / CLAIM / RIGHTS GRAPHS
  engine_v17/models.py (lattice), claim_graph.py, rights_graph.py, compiler.py
    │
    ▼
DECISION MODEL → report-renderer/render_report.py → HTML + PDF
```

**Invariant:** `execution complete ≠ evaluation valid`. `CombinedStatus(execution, evidence)` (`engine_v17/status.py`) never collapses to `SUCCESS`.

## 2. Mission Model

`engine_v17/mission.py:EvaluationMission`

| Field | Required | Description |
|-------|----------|-------------|
| `evaluation_id` | yes | Normalized patent ID (e.g., `US8527057`) |
| `target` | yes | Source artifact path |
| `target_type` | yes | `patent`/`publication`/`submission`/`mixed` |
| `mission` | yes | Immutable sentence, sha256 hash |
| `scope` | yes | `full-pipeline` etc., slices DAG |
| `framework_version` | yes | `v1.7` |
| `execution_version` | yes | `autoprompt-1.0.3-opencode` |
| `evidence_policy` | yes | `schemas/evidence-contract` ref |
| `required_domains` | yes | Skill IDs from registry |
| `output_contract` | yes | `evaluation_dir` + required artifacts |
| `run_id` | auto | `RUN-<id>-<timestamp>` |

Writes `evaluation-mission.json` with `mission_hash` + `mission_bytes`. Workers verify pointer before acting (`workers.py:verify_mission_pointer`).

## 3. DAG

`engine_v17/dag.py:build_dag` — 9 nodes, 13 hard edges, validated against `schemas/skill_registry.json` via `validate_dag_against_registry`. Sliced to `required_domains` + transitive hard deps, `launch_groups` = topological rank.

```
0:[gather-submission]  1:[analyze-technology]  2:[patent-landscape, literature-search, market-opportunity]
3:[novelty-search, identify-partners]  4:[compile-report]  5:[render-report]  6:[review+verification]  7:[arbitration]
```

`DAG_DIAGRAM` in `dag.py:150`.

## 4. Workers

`engine_v17/workers.py:WORKER_PERSONA` maps each DAG node to an `ap-*` persona. `dispatch_worker` verifies mission pointer, routes to `_worker_*`, records `ExecutionLedger` entry with `source_type` (`external` vs `derived` vs `ledger`). `_ensure_claim_mapping` guarantees `claim-mapping.json` regardless of retrieval method (P3).

`hermetic_fetcher.py:make_hermetic_fetcher` provides 4-type mocked payloads (patent HTML, Crossref JSON, WorldBank JSON, partner HTML) for hermetic tests.

## 5. Evidence

`engine_v17/evidence_gate.py:SCHEMAS` (`prior_art_disclosure`, `literature_disclosure`, `market_sizing`, `commercial_adoption`, `partner_fit`) + `SourceObject` (`source_identity`, `locator`, `execution_id`, `independence_lineage_id`) → `apply_evidence_sufficiency_gate`. Live adapters `live_adapters.py:run_live_phase_adapters` produce `raw-*.html/json`, `parsed-domain-evidence.json`, `claim-mapping.json`, `adapter-evidence-decisions.json`.

Ontology: `external source → SourceObject → Evidence item → worker interpretation → Proposition → Review` (E1 counts only `external`).

## 6. E0–E9

`epistemic_gates.py:49` — definitions, `check_E0` … `check_E9`, `run_all_gates`, `gates_blocking_delivery`. See `README.md#E0–E9` for table. `E3` = Sufficiency Gate, `E7/E8` consume `review-ledger.json`.

## 7. Proposition Review Matrix

`orchestrator_autoprompt.py:328` — for every proposition `P-*` (5 in US8527057), `independent_review` (`ap-reviewer`, not blind) + `fresh_verification` (`ap-fresh-verifier`, blind) → `proposition-review-matrix.json` (per-proposition `criticality=critical`, `reviewer_verdict`, `verifier_verdict`). All 5 must PASS for `E7/E8` PASS, else `BLOCKED` with `missing=[…]`. `review-ledger.json` persists 10 records (`is_blind`, `is_independent`, `evidence_refs`).

## 8. Provenance

Manifest `run-manifest.json`: `execution_mode` (`REAL_AUTOPROMPT` vs `LEGACY_FALLBACK`), `epistemic_mode` (`FULL_CONTROLLER` vs `LEGACY`), `review_mode` (`INDEPENDENT`), `verification_mode` (`BLIND_FRESH`), `lane_dispatch_log` (9 entries, group/persona/execution_id), `all_lanes_real`, `proposition_review_matrix`, `epistemic_gates`, `combined_status`. Benchmark `benchmarks/harness.py` proves B/C differ via manifest 4-tuple.

## 9. Artifact Flow

```
evaluation-mission.json → execution-plan.json → run-manifest.json (early)
  → per-lane artifacts (submission, technology-profile, landscape, literature, market, partners)
  → claim-mapping.json (deterministic)
  → proposition-ledger.json / evidence-graph.json / claim-graph.json / rights-graph.json
  → epistemic-gate-report.json (first, PENDING)
  → review-ledger.json + proposition-review-matrix.json → epistemic-gate-report.json (second, real)
  → combined-status.json / coverage-report.json
  → scores-manifest.json (target_patent + evidence_items + gauges)
  → report-*.md → report-*.html / .pdf
```

No recursion: `permission.task` denies non-`ap-*`, `skill: deny`, `AUTOPROMPT-RUN-MARKER` verified.

## 10. Configuration

`autoprompt/ief.json` — skill discovery, state paths (`~/.ief-runs/<id>`), review/verifier, concurrency `tokensaver/6`, retry `2/exponential/60s`, `evidence_debt_is_structured_task`. `~/.config/opencode/autoprompt.opencode.json` — `subagent_depth=4`, `share=disabled`.

## 11. Validation

`tests/test_real_dispatch.py` (11), `tests/test_autoprompt_integration.py` (11), `tests/test_failure_modes.py` (15), `Test-report-results/tests_v17` (113), `report-renderer/tests` (63) → 214 total. `benchmarks/harness.py` A/B/C with overclaim `0.20` PASS.

## 12. Known Limitations

- `verify.sh` semantic scan: `Executive Summary|v1.7 Control State|Original Submission not emitted (88 nodes)` — pre-existing fixture renderer mismatch hidden previously by contamination abort; new runs render correctly (74K HTML).
- EPO OPS live path requires credentials for non-hermetic runs (fallback graceful).
