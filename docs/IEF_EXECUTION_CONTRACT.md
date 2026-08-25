# IEF Execution Contract

**Version:** 1.0.0  
**Framework:** invention-evaluation-framework v1.7  
**Execution OS:** Autoprompt 1.0.3 (OpenCode provider, inherited-only effort)  
**Status:** Active integration contract

## 1. Purpose

This document is the **machine-readable execution contract** that binds the three separated authorities:

- **Autoprompt** — execution operating system (what runs, in what order, by which worker, with which dependencies, how verified)
- **IEF Domain Orchestrator** (`skills/SKILL-Orchestrator.md` + `engine_v17/orchestrator.py`) — domain policy authority (which IEF skills are required, their I/O contracts, evidence constraints, DAG)
- **Evidence Controller** (`engine_v17/evidence_gate.py` + `engine_v17/epistemic_gates.py` + `engine_v17/coverage.py`) — epistemic authority (does evidence justify the proposition)

No single authority may collapse the other two.

## 2. Contract Identity

```yaml
contract_id: IEF-EXECUTION-CONTRACT-v1
framework_version: "v1.7"
execution_version: "autoprompt-1.0.3-opencode"
contract_version: "1.0.0"
```

## 3. Evaluation Mission

Every evaluation run is initiated by an **Evaluation Mission** object (see `schemas/evaluation-mission.schema.json`):

| Field | Required | Description |
|-------|----------|-------------|
| `evaluation_id` | yes | Canonical normalized patent/invention ID, e.g. `US8527057` |
| `target` | yes | Absolute or evaluation-relative path to source artifact |
| `target_type` | yes | `patent` / `publication` / `submission` / `mixed` |
| `mission` | yes | Exact natural-language mission text (one sentence, immutable) |
| `scope` | yes | `full-pipeline` / `landscape-only` / `novelty-only` / `market-only` / `custom` |
| `framework_version` | yes | e.g. `v1.7` |
| `execution_version` | yes | e.g. `autoprompt-1.0.3` |
| `evidence_policy` | yes | Reference to `schemas/evidence-contract.schema.json` |
| `required_domains` | yes | List drawn from `skill_registry.json` skill IDs |
| `dependencies` | auto | Derived from DAG (`engine_v17/dag.py`) |
| `success_criteria` | yes | Typed list: completion + evidence status thresholds |
| `constraints` | no | Temporal scope, jurisdiction, budget, model |
| `temporal_scope` | no | `pre_filing` date window, grant date, critical date |
| `required_verification` | yes | `independent_review` + `fresh_verification` flags |
| `escalation_rules` | yes | Evidence-debt recovery ladders per skill |
| `output_contract` | yes | Absolute `evaluation_dir` + required artifacts |

The mission is **immutable after dispatch**. Workers may not redefine it.

## 4. Mission Lifecycle

```
USER REQUEST
    │
    ▼
AUTOPROMPT L0 CONDUCTOR (receives mission text, creates PROMPTS.txt pointer)
    │
    ▼
IEF MISSION ADAPTER (engine_v17/autoprompt_adapter.py)
    │  validates mission → builds typed EvaluationMission
    │  resolves evaluation_dir, run_id, framework_version
    ▼
IEF DOMAIN ORCHESTRATOR
    │  selects required skills via registry + DAG
    │  emits ExecutionPlan (phases, lanes, dependencies, launch groups)
    ▼
AUTOPROMPT EXECUTION LAYER
    │  L1 scope coordinator → roadmap authors → reviewer + fresh verifier
    │  L1 feature coordinator → L2 managers → L3 executors → L4 leaves
    │  parallel lanes per DAG launch group, spawn-all-then-collect
    ▼
EVIDENCE CONTROLLER (after each phase + pre-compile)
    │  E0 Intake validity
    │  E1 Source integrity
    │  E2 Proposition integrity
    │  E3 Evidence sufficiency (Sufficiency Gate)
    │  E4 Temporal validity
    │  E5 Contradiction check
    │  E6 Analytical validity
    │  E7 Independent review
    │  E8 Fresh verification
    │  E9 Report integrity
    ▼
ARBITRATION (ap-arbiter, only on reviewer/verifier disagreement)
    ▼
DECISION MODEL (scores-manifest.json + evidence-graph.json)
    ▼
REPORT RENDERER (report-renderer/render_report.py)
    ▼
UNIFIED RUN LEDGER (run-manifest.json + execution-ledger.json)
```

There is **exactly one top-level orchestration authority** per run: Autoprompt. No worker spawns a new top-level Autoprompt run. No recursive `autoprompt → orchestrator → autoprompt` loop.

## 5. Skill Execution Contract

Every IEF skill exposes a machine-readable contract (see `schemas/skill-contract.schema.json` and `schemas/skill_registry.json`):

- `skill_id` (e.g. `patent-landscape`)
- `purpose`, `inputs`, `outputs`
- `dependencies` (hard/soft, phase IDs)
- `evidence_requirements` (schema IDs, corroboration)
- `required_tools` / `required_data`
- `failure_states`, `retry_behavior`
- `verification_requirements` (independent review / fresh verification / arbiter)
- `downstream_consumers`
- `completion_criteria`
- `evidence_policy` (which epistemic gates apply)

The registry is the single source of truth; skills may not duplicate or extend schemas defined in `engine_v17/evidence_gate.py::SCHEMAS`.

## 6. Execution DAG

The DAG is defined in `engine_v17/dag.py` and validated against `skills/INDEX.md`. Conceptual shape used for lane dispatch:

```
INTAKE (01-02)
   │
   ▼
SOURCE VALIDATION + INVENTION EXTRACTION (03)
   │
   +------------+------------+
   |            |            |
   v            v            v
CLAIMS (05) TECHNOLOGY(03) MARKET(06-07)
   |            |            |
   v            v            v
PRIOR ART  LITERATURE   COMPETITION
   |            |            |
   +------------+------------+
                |
                v
         EVIDENCE GRAPH
                |
    +-----------+-----------+
    |           |           |
    v           v           v
 NOVELTY    RIGHTS    COMMERCIAL
    |           |           |
    +-----------+-----------+
                |
                v
        PROPOSITION AUDIT
                |
                v
        INDEPENDENT REVIEW (E7)
                |
                v
        FRESH VERIFICATION (E8)
                |
                v
           ARBITRATION
                |
                v
          DECISION MODEL
                |
                v
          REPORT RENDERER (10)
```

- **Launch groups** are computed from topological rank: phases with no unsatisfied hard dependencies dispatch concurrently (spawn-all-then-collect).
- A phase may start **only** when all hard dependencies are `COMPLETED` or `COMPLETED_WITH_EVIDENCE_DEBT`; `BLOCKED` or `FAILED` blocks downstream hard dependents.

## 7. Epistemic Gates (E0–E9)

Autoprompt execution gates and IEF evidence gates are **separate**:

| Gate | Name | Authority | Blocks |
|------|------|-----------|--------|
| E0 | Intake validity | IEF Orchestrator | Can we establish what is being evaluated? |
| E1 | Source integrity | Evidence Controller | Valid, readable, correctly identified, complete sources |
| E2 | Proposition integrity | Evidence Controller | Atomic decomposition, stable ID+version |
| E3 | Evidence sufficiency | Evidence Controller | Each proposition passes Sufficiency Gate |
| E4 | Temporal validity | Evidence Controller | Evidence valid for relevant date/time |
| E5 | Contradiction check | Evidence Controller | Conflicting evidence reconciled |
| E6 | Analytical validity | Evidence Controller | Conclusion follows from evidence |
| E7 | Independent review | Autoprompt ap-reviewer (routed) + IEF reviewer contract | Independent reviewer reproduces/validates |
| E8 | Fresh verification | Autoprompt ap-fresh-verifier (blind) | Fresh verifier independently validates critical findings |
| E9 | Report integrity | Renderer contract (`report-renderer/contract.py`) | Report preserves evidence status, uncertainty, limitations |

**Rule:** `execution complete ≠ evaluation valid`. A run may be `COMPLETE` with `EVIDENCE: PARTIALLY_SUFFICIENT` or `INSUFFICIENT`.

## 8. Execution Status vs Evidence Status

These are **orthogonal** and never collapsed into generic `SUCCESS`:

**Execution Status** (from `engine_v17/execution.py::RunStatus` + `engine_v17/status.py`):
- `COMPLETE`
- `COMPLETED_WITH_EVIDENCE_DEBT`
- `PARTIAL`
- `BLOCKED`
- `FAILED`
- `NOT_STARTED` / `RUNNING`

**Evidence Status** (from `engine_v17/models.py::EpistemicState` + `engine_v17/status.py::EvidenceStatus`):
- `SUFFICIENT` (CONFIRMED PRESENT / CONFIRMED ABSENT with bounded universe)
- `PARTIALLY_SUFFICIENT`
- `INSUFFICIENT` (WORK QUEUE / EXCLUDED)
- `CONTRADICTED`
- `UNAVAILABLE` / `UNAVAILABLE_BY_CONSTRAINT`
- `ESCALATED` (ESCALATION_REQUIRED / SEARCH_EXHAUSTED)

A completed execution may legitimately be `(EXECUTION: COMPLETE, EVIDENCE: INSUFFICIENT)`. The renderer must display both.

## 9. Evidence Debt Integration

Unresolved evidence requirements become **structured tasks**, not hallucinations:

```
Evidence Debt
  ├─ recoverable → create ap-researcher / ap-sweeper task via Autoprompt lane
  ├─ ambiguous   → escalate to ap-arbiter
  └─ unavailable-by-constraint → record UNAVAILABLE_BY_CONSTRAINT with barrier_type
```

- Bounded retry: each avenue has max retries (default 2) + timeout (default 60s). Retry exhaustion → `BLOCKED` avenue, not fabricated answer.
- Model confidence ≠ evidence confidence.

## 10. Independent Review / Fresh Verification / Arbitration

```
WORKER RESULT
   ├─→ ap-reviewer (independent, reads mission+roadmap+evidence, not author's verdict)
   ├─→ ap-fresh-verifier (blind, re-derives truth without reading reviewer verdict)
   └─→ on disagreement → ap-arbiter (decides, never waives capability/cov failures)
```

- The agent that produces a material conclusion **must not be the sole validator**.
- Reviewers receive structured evidence references, not prose assertions.

## 11. Run Ledger

Unified ledger answers (see `engine_v17/execution.py::ExecutionLedger` + `engine_v17/status.py`):

- What mission was requested? (PROMPTS.txt hash)
- Which framework / Autoprompt / model ran?
- Which skills / agents / tasks ran, with dependencies?
- Which tasks succeeded / failed / retried?
- Which evidence was retrieved (source_identity, locator, lineage)?
- Which propositions established / unresolved, with barrier_type?
- Which gates passed (E0–E9, coverage gates)?
- What was arbitrated?
- Final execution status + evidence status

No multiple contradictory state sources. `PIPELINE_STATE.md` remains the human version record; `run-manifest.json` + `execution-ledger.json` are the machine ledger.

## 12. Configuration

Autoprompt is configured for IEF via:

- `~/.config/opencode/skills/autoprompt/SKILL.md` (execution OS, installed)
- `~/.config/opencode/autoprompt.opencode.json` (activation profile, inherited-only)
- `autoprompt/ief.json` (repo-local IEF mission/DAG/skill-path/run-state configuration)
- `schemas/*.schema.json` (typed contracts)
- `engine_v17/autoprompt_adapter.py` (mission↔execution translation)

Transient run-state lives in `~/.ief-runs/<evaluation-id>/` **or** `evaluations/<id>/` per `IEF_EXECUTION_CONTRACT.md` §3 output_contract. Governance artifacts `PROMPTS.txt`, `ROADMAP.md`, `GATELOG.md` live at the run governance root **outside** the target working tree and never appear in its diff.

## 13. Failure Handling

See `engine_v17/epistemic_gates.py` and `engine_v17/review.py` for the 15 mandatory failure-mode behaviors:

1. source unavailable → BLOCKED avenue, escalate
2. source rate-limited → TRANSIENT_FAILURE, bounded retry
3. malformed source → REQUIRES_VERIFICATION → BLOCKED if unrecoverable
4. incomplete source → E1 fail, record barrier
5. contradictory sources → E5, RECONCILIATION_REQUIRED
6. insufficient evidence → E3 fail → evidence debt task
7. agent timeout → FAILED task, retry with backoff
8. worker failure → FAILED lane, dependent lanes blocked
9. retry exhaustion → BLOCKED → EXHAUSTED proposition (not evidence)
10. verifier disagreement → arbiter
11. reviewer disagreement → arbiter
12. unsupported conclusion attempt → E6 fail, EXCLUDED from findings
13. claim mapping disagreement → E2 fail, new proposition version required
14. partial pipeline completion → PARTIAL execution, INSUFFICIENT evidence
15. report rendering failure → E9 fail, BLOCKED delivery

In all cases: `missing evidence ≠ negative evidence`, `execution failure ≠ evidence of absence`, `model confidence ≠ evidence confidence`.

## 14. Backward Compatibility

Existing IEF workflows (`engine_v17/orchestrator.py::run`, `run_generic`, `install.sh`, `verify.sh`, `report-renderer/*`) continue to work. The adapter layer (`engine_v17/autoprompt_adapter.py`) provides compatibility shims; no deletion of old architecture until replacement is validated.

## 15. Security

Autoprompt source was inspected for hardcoded credentials, unsafe shell execution, path traversal, destructive commands, unexpected network calls, telemetry, and hidden installation behavior. No credentials are committed. No destructive commands are executed without explicit user authorization per Autoprompt §11.

## 16. Versioning

This contract is versioned separately from the framework. Changes require updating `contract_version` and re-validating `verify.sh`.

