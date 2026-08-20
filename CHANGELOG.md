# Changelog

## Phase 3 Hardening / Autoprompt Integration — 2026-08-20

**Engineering Operational · Autoprompt Integration Complete · Evidence Controller Operational · Real Multi-Agent Execution Proven**

This release completes the Autoprompt execution/orchestration integration while preserving IEF as the domain and epistemic authority.

### Added

- **Real Autoprompt worker dispatch** (`engine_v17/orchestrator_autoprompt.py:35`): `EvaluationMission` → `ExecutionPlan` (DAG launch groups) → L1 coordinators → L2 managers → L3 executors (`ap-scribe`, `ap-scoper`, `ap-researcher`, `ap-synthesizer`) → L4 leaves (`ap-reviewer`, `ap-fresh-verifier`, `ap-arbiter`) via `spawn-all-then-collect` (max 6, bounded retry). `REAL_AUTOPROMPT` with `all_lanes_real=true`, no silent `LEGACY_FALLBACK` (explicit benchmark mode only), no recursion (`skill: deny` + `permission.task`).
- **Mission system** (`engine_v17/mission.py`, `schemas/evaluation-mission.schema.json`): typed, immutable, hash-verified.
- **DAG** (`engine_v17/dag.py`): 9 nodes, 13 hard edges, validated against `schemas/skill_registry.json`, sliced to mission, launch groups = topological rank.
- **Evidence provenance** (`engine_v17/status.py`): `CombinedStatus(execution, evidence)` — `COMPLETED_WITH_EVIDENCE_DEBT / INSUFFICIENT` is valid, never collapsed to `SUCCESS`.
- **E0–E9** (`engine_v17/epistemic_gates.py`): intake → source → proposition → sufficiency → temporal → contradiction → analytical → independent review → fresh verification → report.
- **Independent review matrix** (`engine_v17/review.py`, `engine_v17/orchestrator_autoprompt.py:328`): every material proposition (5/5 in US8527057) gets `ap-reviewer` + blind `ap-fresh-verifier`, persisted to `proposition-review-matrix.json` (criticality explicit) + `review-ledger.json` (10 records, `is_blind`/`is_independent`), `E7/E8` BLOCK when coverage incomplete.
- **Deterministic claim mapping** (`engine_v17/workers.py:_ensure_claim_mapping`): analytical contract, not retrieval side-effect; `claim-mapping.json` always produced (`WORK QUEUE` if incomplete).
- **Source ontology** (`epistemic_gates.py:75`): `external` vs `derived`/`worker_output`/`provenance`/`ledger`; `E1` counts 7 external sources (3 derived not counted).
- **Benchmark provenance 4-tuple** (`benchmarks/harness.py:91`, `orchestrator_autoprompt.py:103`): `execution_mode`/`epistemic_mode`/`review_mode`/`verification_mode`; Variants A `LEGACY_FALLBACK/LEGACY`, B `REAL_AUTOPROMPT/IEF_STANDARD`, C `REAL_AUTOPROMPT/FULL_CONTROLLER/INDEPENDENT/BLIND_FRESH`; overclaim metric corrected (`overclaim_rate = debt in findings / debt`, audit mentions not counted).
- **Hermetic live adapters** (`engine_v17/hermetic_fetcher.py`, `engine_v17/live_adapters.py`): 4-type mocked payloads (patent HTML, Crossref JSON, WorldBank JSON, partner HTML) → `SourceObject` → `evidence_gate` → ledger.
- **Schemas & registry** (`schemas/`, `autoprompt/ief.json`): `evaluation-mission`, `skill-contract`, `evidence-contract`, `skill_registry.json` (9 skills).
- **Tests:** `tests/test_real_dispatch.py` (11), `tests/test_autoprompt_integration.py` (11), `tests/test_failure_modes.py` (15); total 214 passing (11+27+113+63), 3× reproducibility.
- **Documentation:** `README.md` (590 lines, architecture, DAG, workers, E0–E9, evidence debt, proposition review, claim mapping, validation status, benchmark, quick start, repository map), `docs/ARCHITECTURE.md`, `docs/INTEGRATION-AUTOPROMPT.md`, `IEF_EXECUTION_CONTRACT.md`.
- **Fixture provenance fix:** `evaluations/us8527057-v17*/scores-us8527057-v17.json` now include `target_patent.publication_number=US8527057B2` (legitimate schema repair; contamination gate now correctly treats US8527057 content as legitimate).

### Changed

- `skills/SKILL-Orchestrator.md`: refactored from linear executor to domain-policy router (Autoprompt is execution, IEF is policy).
- `engine_v17/__init__.py`: re-exports mission/dag/status/gates/review/adapter.
- `.gitignore`: `.ief-runs/`, `PROMPTS.txt`, `ROADMAP.md`, `GATELOG.md`, `.autoprompt/`, `skills/autoprompt-skill-main.zip`.
- `skills/GLOSSARY.md`: added Autoprompt Integration — E0-E9 Hardening terminology (14 terms).

### Validation

- **US8527057 real Autoprompt run:** `REAL_AUTOPROMPT/FULL_CONTROLLER/INDEPENDENT/BLIND_FRESH`, 9 lanes, 10 reviews, `E0-E2 PASSED`, `E3 FAILED` (5/5 insufficient, correct), `E7/E8 PASSED` (5/5 matrix), `claim-mapping.json` deterministic, 7 external sources, `COMPLETED_WITH_EVIDENCE_DEBT/INSUFFICIENT`, no recursion, HTML 74K + PDF 509K.
- **Benchmark:** A 0.88 → B/C 1.00 completion without overclaim increase (0.20 steady, gate PASS); retry counts differ (A 01:1…08:1 vs B/C 02:1,03:1,04:2,05:2,06:1,07:1,08:1,09:1).
- **Multi-run:** 3× consistent, no recursion.

### Known Limitations

- `verify.sh` semantic scan: `Executive Summary|v1.7 Control State|Original Submission not emitted (88 nodes)` — pre-existing fixture renderer mismatch (hidden previously by contamination abort); new runs render correctly.
- EPO OPS live path requires credentials for non-hermetic runs (fallback graceful).

### Roadmap Next

- Validation corpus expansion (8 epistemic conditions) · Evaluation science (A/B/C across corpus: claim-mapping accuracy, sufficiency accuracy, review agreement, reproducibility, runtime/cost) · Product (executive-first reports, interactive graph, decision dashboard).

---

## v1.8 — Renderer Contract + Visual QA (2026-08-16)

- `report-renderer/contract.py` (pre-render integrity gate: target identity, evidence provenance, epistemic consistency, proposition registry, contamination)
- `report-renderer/visual_qa.py` (structural + visual QA, TOC page numbers, footer, watermark)
- `verify.sh` semantic scans

## v1.7 — Evidence Controller + Recovery (2026-08-15)

- `engine_v17/models.py` (lattice), `engine_v17/execution.py` (ledger), `engine_v17/recovery.py`, `engine_v17/claim_graph.py`, `engine_v17/rights_graph.py`, `engine_v17/constraints.py`, `engine_v17/coverage.py`

## v1.6 — Tesla US433700 validation

- Evidence architecture, causal bridge, motivation object

