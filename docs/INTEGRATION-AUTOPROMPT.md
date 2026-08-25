# IEF × Autoprompt Integration

**Version:** 1.0.0  
**Date:** 2026-08-20  
**Framework:** v1.7  
**Execution OS:** Autoprompt 1.0.3 (OpenCode, inherited-only)

## 1. Architecture

```
USER EVALUATION REQUEST
         │
         ▼
AUTOPROMPT EXECUTION LAYER  (L0 conductor → L1 coordinators → L2 manager → L3 executors → L4 leaves)
  owns: mission decomposition, planning, dependency mgmt, scheduling, parallel lanes,
        worker lifecycle, review routing, ledger, retry, arbitration
         │
         ▼
IEF DOMAIN ORCHESTRATOR  (skills/SKILL-Orchestrator.md + engine_v17/orchestrator.py + orchestrator_autoprompt.py)
  owns: which domain skills required, I/O contracts, DAG, evidence constraints, phase checklist
         │
         ▼
IEF DOMAIN SKILLS  (skills/skill-02…10)
         │
         ▼
EVIDENCE CONTROLLER  (engine_v17/evidence_gate.py + epistemic_gates.py + coverage.py)
  owns: sufficiency, debt, contradiction, temporal validity, claim mapping
         │
         ▼
EVIDENCE / PROPOSITION / CLAIM SYSTEM  (engine_v17/models.py, compiler.py, claim_graph.py, rights_graph.py)
         │
         ▼
INDEPENDENT REVIEW  (ap-reviewer) → FRESH VERIFICATION  (ap-fresh-verifier, blind) → ARBITRATION  (ap-arbiter)
         │
         ▼
DECISION MODEL  (scores-manifest.json + evidence-graph.json + constraint-report.json)
         │
         ▼
REPORT RENDERER  (report-renderer/render_report.py → HTML + PDF with contract.py + visual_qa.py)
```

**Invariant:** `execution complete ≠ evaluation valid`. A run may be `COMPLETE` with `EVIDENCE: INSUFFICIENT`. Never collapse into generic `SUCCESS`.

## 2. Responsibility Split

| Autoprompt | IEF Orchestrator | Evidence Controller | Report Engine |
|------------|------------------|---------------------|---------------|
| What needs to execute, in what order, by which worker, with which deps, and how verified? | Which domain skills required, what I/O contracts, what evidence constraints? | Does evidence actually justify the proposition? | How to render the verified result? |

## 3. Directory Structure

```
invention-evaluation-framework/
├── docs/IEF_EXECUTION_CONTRACT.md     # human contract
├── schemas/
│   ├── evaluation-mission.schema.json # mission contract
│   ├── skill-contract.schema.json     # skill I/O contract
│   ├── evidence-contract.schema.json  # evidence contract
│   └── skill_registry.json            # machine registry (9 skills)
├── autoprompt/
│   ├── ief.json                       # IEF-specific Autoprompt config
│   └── README.md
├── engine_v17/
│   ├── mission.py                     # EvaluationMission factory
│   ├── dag.py                         # Execution DAG + launch groups
│   ├── status.py                      # ExecutionStatus vs EvidenceStatus
│   ├── epistemic_gates.py             # E0–E9
│   ├── review.py                      # independent review / fresh verify / arbitration
│   ├── autoprompt_adapter.py          # mission ↔ ledger adapter
│   ├── orchestrator.py                # legacy runner (preserved)
│   └── orchestrator_autoprompt.py     # new Autoprompt-aware runner (backward-compatible)
├── benchmarks/
│   └── harness.py                     # A/B/C comparison (overclaim gate)
├── tests/
│   ├── test_autoprompt_integration.py # 11 integration tests
│   └── test_failure_modes.py          # 15 failure-mode tests
├── evaluations/<id>/                  # evaluation artifacts (versioned)
├── .ief-runs/<id>/ or ~/.ief-runs/<id>/ # transient governance (gitignored)
│   ├── PROMPTS.txt
│   ├── ROADMAP.md
│   └── GATELOG.md
└── skills/
    ├── SKILL-Orchestrator.md          # refactored domain-policy router
    ├── skill-02-gather-...            # domain skills (unchanged contracts)
    └── ...
```

Autoprompt skill itself lives at `~/.config/opencode/skills/autoprompt/` (installed, 25 personas, `autoprompt.opencode.json` activation profile). Not duplicated in repo except as `skills/autoprompt-skill-main.zip` reference.

## 4. Configuration

**Autoprompt (execution OS):**
```bash
bash /tmp/autoprompt_extract/autoprompt-skill-main/scripts/install/install.sh opencode
# installs to ~/.config/opencode/skills/autoprompt/SKILL.md
#           ~/.config/opencode/agents/ap-*.md (25)
#           ~/.config/opencode/autoprompt.opencode.json (subagent_depth=4, share=disabled, task: ap-* allow)
```

**IEF for Autoprompt:**
- `autoprompt/ief.json` — IEF skill paths, execution state paths, review/verifier, concurrency (tokensaver, max_subs=6, DAG launch groups), retry (2, exponential, 60s), evidence-sensitive handling
- `schemas/skill_registry.json` — single source of truth for skill I/O, validated against `skill-contract.schema.json`
- `engine_v17/autoprompt_adapter.py` — typed translation; no recursive orchestration (`skill: deny` on every persona, `permission.task` denies non-ap-*)

**Transient state:** `~/.ief-runs/<evaluation-id>/` preferred, `.ief-runs/<evaluation-id>/` fallback. Governance artifacts never appear in target diff. `.gitignore` updated.

## 5. Mission Lifecycle

1. User request → L0 conductor creates `PROMPTS.txt` (mission hash)
2. `IEF Mission Adapter` validates, builds `EvaluationMission`, writes `evaluation-mission.json`
3. `IEF Domain Orchestrator` selects skills via registry + DAG, emits `execution-plan.json` (launch groups)
4. Autoprompt `ap-scope-coordinator` → roadmap authors → reviewer + fresh verifier; `ap-feature-coordinator` → lanes per launch group (spawn-all-then-collect)
5. Each phase → Evidence Controller E0–E6; post-compile → E7–E9; coverage gates (`coverage.py`)
6. On reviewer/verifier disagreement → `ap-arbiter` (never waives coverage/verification)
7. Decision model → Report Renderer (contract + visual QA)
8. Unified ledger: `run-manifest.json` + `execution-ledger.json` + `review-ledger.json` + `execution-plan.json` + `evaluation-mission.json` + `epistemic-gate-report.json` + `combined-status.json`

## 6. Execution DAG

Derived from `skills/INDEX.md` + `skill_registry.json`, validated by `dag.validate_dag_against_registry()`. Sliced to mission's `required_domains` plus transitive hard deps. Launch groups = topological rank.

Full-pipeline groups:
```
0: [gather-submission]
1: [analyze-technology]
2: [patent-landscape, literature-search, market-opportunity]  (landscape is hard dep for novelty, so novelty moves to next group)
3: [novelty-search, identify-partners]
4: [compile-report]
5: [render-report]
6: [independent review + fresh verification (concurrent)]
7: [arbitration if needed]
```

See `engine_v17/dag.py::DAG_DIAGRAM`.

## 7. Skill Contracts

Each skill exposes `skill_id, purpose, inputs, outputs, dependencies (hard/soft/blocks), evidence_requirements (SCHEMAS keys), required_tools, failure_states, retry_behavior, verification_requirements, downstream_consumers, completion_criteria, epistemic_gates, coverage_gate`. Single registry prevents drift.

## 8. Evidence Gates (E0–E9)

| Gate | Question | Authority | Blocks |
|------|----------|-----------|--------|
| E0 | What is being evaluated? | Orchestrator | intake invalid |
| E1 | Sources valid/complete? | Controller | source_integrity |
| E2 | Atomic propositions? | Controller | proposition_integrity |
| E3 | Sufficient evidence? | Controller (Sufficiency Gate) | evidence_sufficiency |
| E4 | Valid for date/time? | Controller | temporal_validity |
| E5 | Conflicting evidence? | Controller | contradiction |
| E6 | Conclusion follows? | Controller (premise map) | analytical_validity |
| E7 | Independent review validates? | ap-reviewer | review |
| E8 | Fresh verifier validates? | ap-fresh-verifier (blind) | verification |
| E9 | Report preserves uncertainty? | Renderer contract | report_integrity |

Implemented in `engine_v17/epistemic_gates.py::run_all_gates`. Execution gates (Autoprompt) and evidence gates (IEF) are separate.

## 9. Status Separation

- **Execution:** NOT_STARTED / RUNNING / COMPLETE / COMPLETED_WITH_EVIDENCE_DEBT / PARTIAL / BLOCKED / FAILED
- **Evidence:** SUFFICIENT / PARTIALLY_SUFFICIENT / INSUFFICIENT / CONTRADICTED / UNAVAILABLE / UNAVAILABLE_BY_CONSTRAINT / ESCALATED

`CombinedStatus` (`engine_v17/status.py`) makes both explicit. `missing evidence ≠ negative evidence`, `execution failure ≠ evidence of absence`.

## 10. Evidence-Debt Integration

Debt → structured task:
- recoverable → `ap-researcher`/`ap-sweeper` lane (bounded retry)
- ambiguous → `ap-arbiter` escalation
- unavailable-by-constraint → `UNAVAILABLE_BY_CONSTRAINT` + `barrier_type`

Agents may not invent answers. Retry exhaustion → `BLOCKED` avenue → `EXHAUSTED` proposition (not evidence).

## 11. Review / Verification / Arbitration

`engine_v17/review.py` enforces: reviewer ≠ author, verifier ≠ author, verifier blind to author's verdict, arbiter never waives capability/coverage/verification failures. Fake independence raises `ValueError`.

## 12. Run Ledger

Unified ledger (`execution-ledger.json` + `run-manifest.json` + `execution-plan.json` + `evaluation-mission.json` + `review-ledger.json` + `epistemic-gate-report.json` + `combined-status.json`) answers all 14 questions in `docs/IEF_EXECUTION_CONTRACT.md §11`. No contradictory state sources.

## 13. Backward Compatibility

`engine_v17/orchestrator.py::run` and `::run_generic` are preserved. New entry point is `engine_v17/orchestrator_autoprompt.py::run_with_autoprompt`. Existing CLI, tests, artifacts, claim mapping, evidence structures, renderer, and `install.sh`/`verify.sh` continue to work via the adapter shim.

## 14. Benchmark

`benchmarks/harness.py` runs A (`LEGACY_FALLBACK/LEGACY`) / B (`REAL_AUTOPROMPT/IEF_STANDARD`) / C (`REAL_AUTOPROMPT/FULL_CONTROLLER`) on existing evaluations, measuring execution completion, evidence/proposition coverage, overclaim rate (must not increase), unsupported inference, debt resolution, runtime, retry counts, reproducibility. Preserves distinction false analogy / unsupported conclusion / legitimate discovery / evidence insufficiency. Verified on US8527057 (hardened): A 0.88 vs B/C 1.00 completion without overclaim increase (0.20 steady, gate PASS), 4-mode provenance explicit, retry counts differ (A 01:1…08:1 vs B/C 02:1,03:1,04:2,05:2,06:1,07:1,08:1,09:1).

## 15. Troubleshooting

- `INVALID-BRIEF` → mission hash mismatch; re-validate `evaluation-mission.json` vs `PROMPTS.txt`
- `INVALID-DISPATCH` → worker dispatched outside active Autoprompt run; check `AUTOPROMPT-RUN-MARKER`
- `fake independence` → reviewer == author; fix dispatch to use distinct `ap-*` persona
- `BLOCKED: artifact_destination` → parent of `evaluation_dir` missing; create it first
- `RenderContractFailure` → scores missing `target_patent` or contamination; see `report-renderer/contract.py`
- `DAG cycle` → hard edge cycle in `skill_registry.json`; validate with `validate_dag_against_registry()`

## 16. No Recursive Orchestration

Exactly one top-level authority per run: Autoprompt. Workers never spawn new Autoprompt runs. Enforced by `permission: { task: { "*": "deny", "ap-*": "allow" }, skill: deny }` on every persona.

## 17. Security

Inspected `autoprompt-skill-main` for hardcoded credentials, unsafe `rm -rf /`, path traversal, `curl | sh`, telemetry, hidden install behavior. Only credential references are in tests (credential-free environment checks). No secrets committed. No destructive commands without explicit user authorization per Autoprompt §11. Transient state is gitignored.
