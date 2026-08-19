# v1.9 Handoff — Invention Evaluation Framework

**Branch:** `v1.9-upgrade` (from `/home/forsythe/Desktop/tools/invention-evaluation-framework`)
**Status:** Plan A tasks A1–A4 committed; A5 test file written, not yet committed/implemented.
**Intent:** framework-level upgrade (not report patches). All six plans approved by the user.

---

## Where to find everything

- **Plans (source of truth):** `docs/superpowers/plans/2026-08-19-v19-plan-<letter>-<name>.md` (A–F). Each has TDD steps with exact code, expected outputs, commit messages.
- **Progress ledger:** `.superpowers/sdd/v1.9-upgrade/progress.md` (I was maintaining it; may be stale — trust `git log` instead).
- **Commits so far** (HEAD = `7bd13d8`):
  - `eac442d` docs: add v1.9 implementation plans A-F
  - `7f9f951` feat(engine): Proposition carries epistemic/recovery lattice and scope
  - `87e1444` feat(engine): add transition_lattice returning separate epistemic/recovery axes
  - `7bd13d8` feat(engine): evidence debt counts recoverable items only
- **Uncommitted:** `report-renderer/tests/test_lattice_contract.py` (Task A5's failing test, already written).

## Repo conventions (critical — the plans were written against an idealized version)

- Repo root is `/home/forsythe/Desktop/tools/invention-evaluation-framework`. Engine = `engine_v17/`, renderer = `report-renderer/`. Tests: `Test-report-results/tests_v17/` (engine, import `engine_v17`) and `report-renderer/tests/` (renderer, `conftest` puts `report-renderer` on `sys.path`; import `contract`).
- `ResolutionState` enum values are **lowercase** (`"established"`, `"unresolved"`, `"escalation_required"`, `"search_exhausted"`, `"blocked"`, `"migration_required"`). Existing tests assert lowercase strings (e.g. `test_us8527057_acceptance.py:31`).
- The **new** v1.9 canonical enums (`EpistemicState`, `RecoveryState`, `Scope`) use **uppercase** values — that's the plan's mandate and matches the renderer contract's existing uppercase constants. Do NOT lowercase them.
- `Proposition` is constructed **positionally** in the orchestrator: `Proposition("P-02-002", "Current legal status", ResolutionState.ESTABLISHED, ...)`. The 3rd positional arg is `state`. **Do not reorder fields** — `state` must stay at position 3.
- `ExecutionLedger.record()` signature: `record(phase_id, action_type, source, query, result_count=None, request="", result_artifact=None, outcome="", candidate_evidence=False, evidence_sufficiency=False) -> ExecutionRecord`. It does NOT accept a `RecoveryAttempt` object. Tests that build attempts must call it with these kwargs and set `attempt.execution_id = rec.execution_id`.
- `ResearchExhaustion.validate()` requires: `sources`, `methods`, `coverage`, `failure_diagnosis`, `troubleshooting`, ≥5 `recovery_strategies` with ≥4 distinct `strategy_class` values, `recursive_recovery_completed=True`, `termination_basis`. For terminal-exhaustion tests, populate all of these (see `Test-report-results/tests_v17/test_recovery.py` lines 36-48 for a working example).
- Python 3.14, pytest 9.0.3, PyYAML 6.0.3 available.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`, `data:`).

## Gotchas already hit (so the next model doesn't re-derive them)

1. **Plan A2 test `test_proposition_from_legacy_state_migrates_to_lattice`**: the plan said `from_dict({"state": "EXHAUSTED"})` → `recovery_state == EXHAUSTED`. But the existing `from_dict` special-cases `"exhausted"` → `MIGRATION_REQUIRED` (a v1.7 quirk), and `MIGRATION_REQUIRED` maps to `(NOT_ESTABLISHED, SEARCH_PENDING)`. **Corrected the test to use `"state": "search_exhausted"`** (the actual enum value), which maps to `EXHAUSTED`. Do not revert this.
2. **`_LATTICE_TO_LEGACY` collision**: both `ESCALATION_REQUIRED` and `BLOCKED` map to `(NOT_ESTABLISHED, ESCALATION_REQUIRED)`, and both `UNRESOLVED` and `MIGRATION_REQUIRED` map to `(NOT_ESTABLISHED, SEARCH_PENDING)`. A dict comprehension lets the later entry win. **Fixed** by building the reverse map explicitly with precedence: `ESCALATION_REQUIRED` over `BLOCKED`, `UNRESOLVED` over `MIGRATION_REQUIRED`. If you see `state` returning `blocked` where `escalation_required` is expected, this is the cause.
3. **`state` is a regular field, not a property**: the plan wanted a derived property, but that broke 4 existing tests (direct construction `Proposition(id=..., state=...)` and the `"exhausted"` → `MIGRATION_REQUIRED` round-trip). **Kept `state` as a field at position 3**; `from_dict` syncs it bidirectionally (lattice fields win when present, else derive lattice from `state`). The plan's A2 test was renamed `test_proposition_from_lattice_fields_sets_state_shim` and uses `from_dict`.
4. **A3 `transition_lattice` is a thin wrapper**: `legacy = transition_state(...); return lattice_from_legacy(legacy)`. It does NOT reimplement the v1.8 invariant logic. That's intentional — preserves all existing behavior.
5. **A4 `calculate_evidence_debt`**: now skips `NONE_REQUIRED` and `UNAVAILABLE_BY_CONSTRAINT`. The old code skipped only `ESTABLISHED` (via `p.state`); the new code uses `p.recovery_state`. `propagate_constraints` still uses `p.state` — leave it (it checks `!= ResolutionState.ESTABLISHED`, which still works).

## Remaining work

**Plan A — Task A5 (in progress):** `report-renderer/contract.py` — replace `EpistemicState` class with canonical values + legacy aliases (`PARTIAL`→`PARTIALLY_ESTABLISHED`, `INFERRED`/`NOT_LOADED`/`UNKNOWN`→`NOT_ESTABLISHED`); add `RecoveryState`, `Scope`; extend `Proposition` dataclass with `recovery_state` + `scope` + `is_recoverable_debt`; update `PropositionRegistry.load` to read new fields with legacy fallback; add `_canonical_state` helper. Test file already written at `report-renderer/tests/test_lattice_contract.py` (6 tests). Then: run `python3 -m pytest report-renderer/tests/ -q` (must stay 57+ passing), commit.

**Plan A — Task A6:** `engine_v17/migration.py` — add `migrate_v18_ledger`. Then migrate `evaluations/US5215088/proposition-ledger.json` (add `epistemic_state`/`recovery_state`/`scope`, keep `status`), apply authoritative fixture states (P-03-003=NOT_ESTABLISHED+ESCALATION_REQUIRED; P-06-005/P-07-001=PARTIALLY_ESTABLISHED+SEARCH_PENDING; P-08-005=PARTIALLY_ESTABLISHED+UNAVAILABLE_BY_CONSTRAINT; P-08-005a/b/c=ESTABLISHED+NONE_REQUIRED; P-08-005d/e/f=NOT_ESTABLISHED+UNAVAILABLE_BY_CONSTRAINT), verify debt=3 (P-03-003, P-06-005, P-07-001), commit.

**Then Plans B–F** in order, each in its own plan file. Key plan-vs-reality adaptations already made for A; expect similar ones in B–F (e.g. Plan B's `QuantitativeClaim` uses string-constant `SourceType` matching the renderer's style; Plan C's guard reads registry state not hardcoded ids; Plan D's `derive_commercial_conclusion` is deterministic; Plan E uses PyYAML; Plan F's `consumer.py` takes dicts whose keys match the Plan B claims array and Plan D/E manifests).

## Verification commands

- Engine suite: `python3 -m pytest Test-report-results/tests_v17/ -q`
- Renderer suite: `python3 -m pytest report-renderer/tests/ -q`
- Both: `python3 -m pytest Test-report-results/tests_v17/ report-renderer/tests/ -q`
- Visual QA: `python3 report-renderer/visual_qa.py 2>&1 | tail -5`

## User's standing instructions

- Execute all six plans without stopping to ask (only stop on genuine blockers). Speed preferred — the user said "knock it out in 15 minutes."
- Plans are complete with code; treat implementation as transcription + testing. Adapt test expectations to the repo's real conventions (lowercase legacy values, positional `state`, `ExecutionLedger.record` kwargs) rather than reverting the repo.
- Commit each green task with a conventional-commit message.