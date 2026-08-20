---
name: invention-evaluation-engine
description: Domain-policy router for the evidence-constrained invention reasoning engine. Autoprompt is the execution authority; this skill is the domain authority — it selects required IEF skills, enforces evidence contracts, DAG dependencies, and epistemic gates. Delegates execution to Autoprompt's L1 coordinators. Not for FTO/infringement — redirect to counsel.
---

# Invention Evaluation Engine — Domain-Policy Router

## Architecture

```
USER EVALUATION REQUEST
         │
         ▼
AUTOPROMPT EXECUTION LAYER (L0 conductor → L1 coordinators → L2/L3/L4 workers)
         │  owns: mission decomposition, planning, scheduling, parallel lanes,
         │        worker lifecycle, review routing, ledger, retry/arbitration
         ▼
IEF DOMAIN ORCHESTRATOR (this skill)
         │  owns: which domain skills are required, I/O contracts, DAG,
         │        evidence constraints, phase checklist, hand-off preservation
         ▼
IEF DOMAIN SKILLS (skills/skill-*/SKILL.md)
         │
         ▼
EVIDENCE CONTROLLER (engine_v17/evidence_gate.py + epistemic_gates.py + coverage.py)
         │  owns: sufficiency, debt, contradiction, temporal, claim mapping
         ▼
INDEPENDENT REVIEW (ap-reviewer) → FRESH VERIFICATION (ap-fresh-verifier) → ARBITRATION (ap-arbiter)
         │
         ▼
DECISION MODEL → REPORT RENDERER
```

**Critical separation:** `execution complete ≠ evaluation valid`. Autoprompt proves execution; IEF proves evidence.

## What this skill IS and IS NOT

| Autoprompt (execution OS) | This skill (domain router) | Evidence Controller |
|---------------------------|----------------------------|---------------------|
| "What needs to execute, in what order, by which worker, with which dependencies, and how verified?" | "Which IEF domain skills are required, what inputs/outputs/contracts, and what evidence constraints apply?" | "Does evidence actually justify the proposition?" |

This skill **does not** perform search, scoring, or legal/financial opinions. It **does not** spawn workers directly — it emits an `EvaluationMission` and `ExecutionPlan` that Autoprompt's L1 coordinators dispatch.

## When to use
- "Evaluate this invention" / "run the full evaluation pipeline"
- "Is my invention patentable and commercially viable?"
- "Start a full commercial + patentability assessment"

## When NOT to use — redirect instead
- FTO / infringement ("can I sell this without being sued?") — stop and explain the novelty-vs-FTO distinction (see `GLOSSARY.md`); scope as separate engagement with counsel. Do not run the novelty pipeline as substitute.
- A single specific analysis (market only, novelty only) — route directly to the relevant sub-skill; this full-pipeline router is still available but will slice the DAG accordingly.

## Execution

### 0. Artifact destination gate — mandatory before analysis

Resolve the output directory before running any phase. Default is the repository's `evaluations/<normalized-invention-id>/` directory. If the user names a folder that path takes precedence. Create the run directory only after verifying its parent exists. The run is not complete until the compiled Markdown report, submission record, proposition ledger, avenue ledger, scores manifest, and (for a full run) styled HTML/PDF are physically present in that directory. A chat response is not a deliverable and must never be treated as substitute for saved artifacts.

Before claiming completion, run a filesystem existence check against every required artifact and report absolute paths. If destination cannot be resolved or written, stop with `BLOCKED: artifact_destination` rather than continuing and presenting an unsaved report.

### 1. Mission construction (IEF Mission Adapter)

Construct the typed `EvaluationMission` via `engine_v17/mission.py::create_mission` and validate against `schemas/evaluation-mission.schema.json`:

- `evaluation_id`, `target`, `target_type`, `mission` (immutable after dispatch), `scope`, `framework_version`, `execution_version`, `evidence_policy`, `required_domains`, `success_criteria`, `output_contract`, `required_verification`, `escalation_rules`, `temporal_scope`, `constraints`, `run_id`

Write `evaluation-mission.json` to the evaluation directory. The mission hash (`sha256`) is the immutable pointer that Autoprompt `PROMPTS.txt` and every worker brief must verify — a mismatch is `INVALID-BRIEF`.

### 2. DAG and execution plan (domain policy)

Build the execution DAG via `engine_v17/dag.py`:

- Canonical DAG is `skills/INDEX.md` + `schemas/skill_registry.json` (validated by `validate_dag_against_registry`).
- Slice DAG to `mission.required_domains` plus transitive hard dependencies.
- Compute `launch_groups` (topological rank) for Autoprompt `spawn-all-then-collect` dispatch.

Write `execution-plan.json` (nodes, edges, topological order, launch groups, diagram). Hard dependencies must be satisfied before a phase runs; soft dependencies may be bypassed with degraded capability noted in the final report.

**DAG launch groups (full-pipeline):**

| Group | Phases (parallel) | Autoprompt lane |
|-------|-------------------|-----------------|
| 0 | gather-submission | L3 ap-scribe / ap-scoper |
| 1 | analyze-technology | L3 ap-scoper |
| 2 | patent-landscape + literature-search + novelty-search (landscape is hard dep for novelty) | L3 ap-researcher + ap-scoper |
| 3 | market-opportunity | L3 ap-researcher |
| 4 | identify-partners | L3 ap-researcher |
| 5 | compile-report | L3 ap-synthesizer |
| 6 | render-report | L3 ap-scribe |
| 7 | independent review + fresh verification (concurrent) | L4 ap-reviewer + ap-fresh-verifier |
| 8 | arbitration (if needed) | L4 ap-arbiter |

A real implementation may merge groups 2–3 where temporal constraints allow; the canonical DAG is the source of truth.

### 3. Autoprompt dispatch (execution authority)

Hand the `EvaluationMission` + `ExecutionPlan` to Autoprompt:

- L0 conductor creates `PROMPTS.txt` (mission pointer), `ROADMAP.md` (executable roadmap), `GATELOG.md` (transitions, provenance, hashes, elapsed time, frontier).
- L1 `ap-scope-coordinator` drives scope topology (bounded: 3 agents/2 rounds; multi-surface: 5/3; unusually-large only with recorded reason).
- L1 `ap-feature-coordinator` drives build lanes per launch group.
- L1 `ap-sweep-coordinator` drives convergence.

Governance artifacts (`PROMPTS.txt`, `ROADMAP.md`, `GATELOG.md`) live at the run governance root **outside** the target working tree (`~/.ief-runs/<evaluation-id>/` or `.ief-runs/<evaluation-id>/`) and never appear in its diff.

**No recursive orchestration:** Autoprompt is the sole top-level authority. Workers do not spawn new top-level Autoprompt runs.

### 4. Evidence-grade preservation at every hand-off

Carry each proposition with its `proposition_id`, `proposition_version`, and evidence state plus avenue records. Never upgrade, strip, or re-scope a proposition at hand-off; any refinement requires a version increment. Unestablished propositions remain in the work queue with search records. Downstream conclusions inherit the weakest unresolved material dependency.

### 5. Phase checklist + epistemic gates

Maintain a phase-completion checklist with explicit `blocked / needs-input` states. After each phase and pre-compile, run the IEF epistemic gates (`engine_v17/epistemic_gates.py`):

- E0 Intake validity — can we establish what is being evaluated?
- E1 Source integrity — valid, readable, correctly identified, sufficiently complete?
- E2 Proposition integrity — atomic decomposition, stable ID+version?
- E3 Evidence sufficiency — each proposition passes Sufficiency Gate?
- E4 Temporal validity — evidence valid for relevant date/time?
- E5 Contradiction check — conflicting evidence reconciled?
- E6 Analytical validity — conclusion follows from evidence?
- E7 Independent review — independent reviewer validates?
- E8 Fresh verification — fresh verifier validates?
- E9 Report integrity — report preserves evidence status, uncertainty, limitations?

These are **evidence gates**, not Autoprompt execution gates. `execution complete` never implies `evaluation valid`.

### 6. Evidence-debt integration with Autoprompt retry

Unresolved evidence requirements become **structured tasks** via the adapter:

- `recoverable` → create `ap-researcher`/`ap-sweeper` task (bounded retry: 2, exponential backoff, 60s timeout)
- `ambiguous` → escalate to `ap-arbiter`
- `unavailable-by-constraint` → record `UNAVAILABLE_BY_CONSTRAINT` with `barrier_type`

Agents may not resolve evidence debt by inventing an answer. Retry exhaustion → `BLOCKED` avenue → `EXHAUSTED` proposition (not evidence). `missing evidence ≠ negative evidence`.

### 7. Independent review → fresh verification → arbitration

Routed by Autoprompt but validated by IEF contracts (`engine_v17/review.py`):

```
WORKER RESULT
   ├─→ ap-reviewer (independent, reads mission+roadmap+evidence, not author's verdict)
   ├─→ ap-fresh-verifier (blind, re-derives truth without reading reviewer verdict)
   └─→ on disagreement → ap-arbiter (decides, never waives coverage/verification failures)
```

The agent that produces a material conclusion must not be sole validator. Reviewers receive structured evidence references, not prose.

### 8. Source extraction completeness gate

Opening or fetching a source is not evidence that its contents were processed. For every source page, extract all decision-relevant structured sections before moving on: citations (including examiner/third-party markers), forward citations, family members and each member's status, assignments/rights events, prosecution metadata, and source's own disclaimers. A source may not generate an `ESCALATION_REQUIRED` item for information visible on the already-open source until the relevant table or section has been parsed and dispositioned.

### 9. Bidirectional evidence-flow gate

New facts discovered in any later phase must trigger an impact review of earlier outputs. Ownership changes must update assignee charts and rights conclusions; family members must receive individual status checks; business-failure evidence must update market and commercialization analysis; newly recovered prior art must update novelty mappings. Record backward edges in the avenue ledger.

### 10. Internal-consistency gate

Before compilation, compare every narrative query, chart footnote, source locator, date range, classification code, and denominator. A mismatch blocks delivery until reconciled. Never present a precise count when its query is blocked, its source is unavailable, or its footnote describes a different query.

### 11. Temporal-normalization gate

Normalize filing counts by the duration of each time bucket. A partial final bucket cannot be interpreted as a trend without an explicit normalization or a `PARTIAL_BUCKET` label. Truncated or incomplete data must not feed a market score, threat, or conclusion.

### 12. Escalation-closure gate

An escalation item is a work instruction, not a deliverable. If the requested classification, business-history check, family status check, or bounded model can be answered from public sources already within the run's scope, execute it before compiling. If it cannot be answered, record the exact blocker, attempted avenues, and decision impact. Do not ship scaffolding formulas or generic queues as if they were completed analysis.

### 13. Report compilation and styled deliverable (mandatory, every run)

Compile via `skills/skill-09-compile-report/SKILL.md` including the reproducible query log and "not legal advice" disclaimers, then render the branded "inventionevaluator" deliverable via `skills/skill-10-render-report/SKILL.md` using `report-renderer/render_report.py`. The styled HTML + A4 PDF (clean cover, TOC with accurate physical page numbers, running footer, watermark, gauges, SWOT, section dividers, search boxes) IS the final deliverable — not an optional extra. The renderer never invents metrics: all gauge/bar values come from the per-run scores manifest, each with a basis proposition_id; charts without established data render labelled placeholder frames.

### 14. Unified run ledger

The ledger answers: what mission, which framework/Autoprompt/model, which skills/agents/tasks, dependencies, which tasks succeeded/failed/retried, which evidence retrieved (source_identity, locator, lineage), which propositions established/unresolved with barrier_type, which gates passed (E0–E9, coverage), what was arbitrated, final execution status + evidence status. Written to `run-manifest.json` + `execution-ledger.json` + `review-ledger.json` + `execution-plan.json` + `evaluation-mission.json`. No multiple contradictory state sources.

## Reference docs (relative to this skill's folder)

- `DIGEST.md` — 5-minute read; the non-negotiables
- `GLOSSARY.md` — full terminology, three-layer epistemic architecture, sufficiency gate, escalation protocol, schema registry
- `INDEX.md` — dependency graph, entry points, dependency types
- `PIPELINE_STATE.md` — version and validation record
- `../IEF_EXECUTION_CONTRACT.md` — execution contract (this integration)
- `../schemas/evaluation-mission.schema.json` — mission schema
- `../schemas/skill-contract.schema.json` — skill contract schema
- `../schemas/evidence-contract.schema.json` — evidence contract schema
- `../schemas/skill_registry.json` — machine-readable skill registry
- `../autoprompt/ief.json` — Autoprompt-for-IEF configuration
- `../engine_v17/mission.py` — mission factory
- `../engine_v17/dag.py` — execution DAG
- `../engine_v17/epistemic_gates.py` — E0–E9
- `../engine_v17/status.py` — execution vs evidence status
- `../engine_v17/review.py` — review/verification/arbitration
- `../engine_v17/autoprompt_adapter.py` — adapter layer

## v1.7 Evidence Recovery Controller + v1.8 Autoprompt Integration

Unresolved propositions are workflow states, not stopping points. Classify missingness, calculate evidence leverage, select a phase-specific recovery policy, execute its escalation ladder, attach a research exhaustion proof, and propagate resulting constraints before compiling conclusions. Active states are `ESCALATION_REQUIRED`, `SEARCH_EXHAUSTED`, and `BLOCKED`; legacy `EXHAUSTED` requires migration review. No downstream conclusion or recommendation may be stronger than its weakest unresolved material dependency.

Evidence-debt recovery tasks are now **Autoprompt lanes**: recoverable debt creates an `ap-researcher`/`ap-sweeper` lane; ambiguous debt escalates to `ap-arbiter`; unavailable-by-constraint is recorded with `barrier_type` and explicitly preserved as uncertainty. Review/verification are **Autoprompt L4 leaves** (`ap-reviewer`, `ap-fresh-verifier`), not a second orchestration pass.

## Boundaries

- No search, no scoring, no legal or financial opinion produced by this skill itself.
- Not a substitute for docketing software or prosecution-tracking.
- Every legal-adjacent statement in outputs carries a "not legal advice" disclaimer.
- This skill never spawns Autoprompt workers directly; it emits mission/plan for Autoprompt to dispatch. Workers never re-invoke this skill.
