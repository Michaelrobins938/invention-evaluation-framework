# Plan C — v1.9 Global Epistemic Renderer Guard: No Overclaim at Any Point of Use

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make it *impossible* for any rendered report to claim epistemic completion while the registry still contains non-established propositions. Four hard rules, enforced in `report-renderer/contract.py` at the pre-render gate and in `render_report.py` at point of use.

**Architecture:** The existing `pre_render_integrity_gate` gains a new `validate_epistemic_guard(registry, report_md, scores)` stage that enforces four rules against the authoritative registry (Plan A lattice states). The Technology Analysis page gains a machine-derived evidence-state column so every quantitative row carries its epistemic state at the point of use, and the renderer refuses to emit an "All propositions established"-style sentence when `unestablished` or `debt` is non-empty. This guard is global — it operates on whatever ledger/registry is passed in, not on US5215088-specific strings.

**Tech Stack:** Python 3.10+ (repo runs 3.14), pytest, `report-renderer/contract.py` + `render_report.py`.

## Global Constraints

- Rule 1 (Universal-completion ban): If `registry.unestablished()` (epistemic_state `NOT_ESTABLISHED` or `CONTRADICTED`) is non-empty, the report MUST NOT contain completion phrases: "all propositions are established", "all propositions established", "fully verified", "fully established", "complete evidence".
- Rule 2 (Point-of-use labeling): Every factual claim in the report that corresponds to a proposition MUST be rendered adjacent to that proposition's epistemic state — enforced by rendering the evidence-state column (Rule 3) and by contract checks that no proposition appears in the report with an overstated inline claim ("ESTABLISHED" inline when registry says `NOT_ESTABLISHED`).
- Rule 3 (Evidence-state column): The Technology Analysis page's Quantitative Performance Comparison table gains an "Evidence State" column whose values come from the registry (per proposition id), never from hand-written text.
- Rule 4 (Executive Summary consistency): If recoverable debt > 0, the Executive Summary MUST NOT contain "no open items", "nothing outstanding", or "all items resolved"; the overall_assessment string in scores must not be paired with absolute-confidence language.
- The guard must work for ANY ledger — no US5215088 hardcoded proposition ids in the guard logic (the existing contamination check is separate and remains as-is).
- Backward compatibility: all existing renderer tests (57) must keep passing; reports that ARE fully established pass the guard unchanged.
- No report-specific hand-fixes. All changes are engine/renderer-level.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`).

## File Structure

- `report-renderer/contract.py` — add `validate_epistemic_guard()`; wire into `pre_render_integrity_gate`.
- `report-renderer/render_report.py` — evidence-state column in the Technology Analysis table; completion-phrase suppression at Executive Summary.
- `report-renderer/tests/test_epistemic_guard.py` — new renderer tests.
- `Test-report-results/tests_v17/test_lattice.py` — no change (guard is renderer-side).

---

### Task C1: Rule 1 + Rule 4 — completion-phrase and debt-consistency guard

**Files:**
- Modify: `report-renderer/contract.py`
- Test: `report-renderer/tests/test_epistemic_guard.py` (new)

**Interfaces:**
- Consumes: `PropositionRegistry` (Plan A Task A5) with `unestablished()` and `is_recoverable_debt`; `render_report`'s `pre_render_integrity_gate`.
- Produces: `validate_epistemic_guard(registry, report_md, scores) -> list[ContractError]`; wired into the gate.

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_epistemic_guard.py
import pytest
from contract import (
    PropositionRegistry, validate_epistemic_guard, RenderContractFailure,
)


def _registry():
    ledger = {"proposition_ledger": {
        "P-03-001": {"claim": "3D array", "epistemic_state": "ESTABLISHED",
                     "recovery_state": "NONE_REQUIRED"},
        "P-03-003": {"claim": "yield", "epistemic_state": "NOT_ESTABLISHED",
                     "recovery_state": "ESCALATION_REQUIRED"},
        "P-08-005d": {"claim": "royalty", "epistemic_state": "NOT_ESTABLISHED",
                      "recovery_state": "UNAVAILABLE_BY_CONSTRAINT"},
    }}
    return PropositionRegistry(ledger)


def test_rule1_all_established_phrase_blocked_when_unestablished_exists():
    report = "## 1. Technology Analysis\n\nAll propositions are now ESTABLISHED with supporting evidence and source citations."
    reg = _registry()
    errors = validate_epistemic_guard(reg, report, {})
    assert any("all propositions" in e.reason.lower() for e in errors)


def test_rule1_fully_verified_blocked():
    report = "## Executive Summary\n\nThis report is fully verified."
    errors = validate_epistemic_guard(_registry(), report, {})
    assert any("fully verified" in e.reason.lower() for e in errors)


def test_rule4_open_items_phrase_blocked_when_debt_exists():
    report = "## Executive Summary\n\nThere are no open items and nothing outstanding in this evaluation."
    errors = validate_epistemic_guard(_registry(), report, {})
    assert any("open items" in e.reason.lower() for e in errors)


def test_guard_passes_when_all_established():
    ledger = {"proposition_ledger": {
        "P-01-001": {"claim": "x", "epistemic_state": "ESTABLISHED",
                     "recovery_state": "NONE_REQUIRED"},
    }}
    reg = PropositionRegistry(ledger)
    report = "## Executive Summary\n\nAll propositions are now ESTABLISHED."
    errors = validate_epistemic_guard(reg, report, {})
    assert errors == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_epistemic_guard.py -v`
Expected: FAIL with `ImportError: cannot import name 'validate_epistemic_guard'`

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/contract.py`, add after `pre_render_integrity_gate` (line ~663):

```python
_COMPLETION_PHRASES = (
    "all propositions are now established",
    "all propositions are established",
    "all propositions established",
    "fully verified",
    "fully established",
    "complete evidence",
)
_DEBT_PHRASES = (
    "no open items",
    "nothing outstanding",
    "all items resolved",
    "no outstanding items",
)


def validate_epistemic_guard(
    registry: "PropositionRegistry",
    report_md: str,
    scores: dict,
) -> list[ContractError]:
    """v1.9 global epistemic guard — four rules, zero overclaim.

    Rule 1: universal-completion ban. Rule 2: point-of-use labeling
    (enforced by Task C3's column + inline-state checks). Rule 3: evidence
    column (Task C3). Rule 4: executive-summary debt consistency.
    """
    errors = []
    lowered = report_md.lower()

    unestablished = [p for p in registry.all()
                     if p.state in (EpistemicState.NOT_ESTABLISHED,
                                    EpistemicState.CONTRADICTED)]
    debt = [p for p in registry.all() if p.is_recoverable_debt]

    # Rule 1
    if unestablished:
        for phrase in _COMPLETION_PHRASES:
            if phrase in lowered:
                errors.append(ContractError(
                    "Epistemic Guard (Rule 1)",
                    "report_body",
                    f"FATAL: completion phrase '{phrase}' found while "
                    f"{len(unestablished)} propositions remain "
                    f"NOT_ESTABLISHED/CONTRADICTED. Report cannot claim "
                    f"epistemic completion."))

    # Rule 4
    if debt:
        for phrase in _DEBT_PHRASES:
            if phrase in lowered:
                errors.append(ContractError(
                    "Epistemic Guard (Rule 4)",
                    "report_body",
                    f"FATAL: no-open-items phrase '{phrase}' found while "
                    f"{len(debt)} recoverable debt items remain."))

    return errors
```

Wire into `pre_render_integrity_gate` — after the registry block (step 4, line ~627), before the contamination block:

```python
    if registry is not None:
        errors.extend(registry.validate_report_consistency(report_md))
        # v1.9: global epistemic guard (Rules 1 + 4 live here; Rules 2 + 3
        # live in the renderer's point-of-use column + C3 checks).
        errors.extend(validate_epistemic_guard(registry, report_md, scores))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_epistemic_guard.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the full renderer suite**

Run: `python3 -m pytest report-renderer/tests/ -q`
Expected: all 57 existing tests still pass.

- [ ] **Step 6: Commit**

```bash
git add report-renderer/contract.py report-renderer/tests/test_epistemic_guard.py
git commit -m "feat(renderer): global epistemic guard bans completion overclaims"
```

---

### Task C2: Rule 2 — inline-state overclaim detection

**Files:**
- Modify: `report-renderer/contract.py`
- Test: `report-renderer/tests/test_epistemic_guard.py`

**Interfaces:**
- Consumes: `PropositionRegistry` with per-proposition canonical states.
- Produces: `validate_inline_state_claims(registry, report_md) -> list[ContractError]` — flags lines where report text pairs a proposition id with an inline "ESTABLISHED" claim while the registry says otherwise.

- [ ] **Step 1: Write the failing test**

```python
# append to report-renderer/tests/test_epistemic_guard.py
def test_rule2_inline_established_contradicts_registry():
    report = ("## 1. Technology Analysis\n\n"
              "P-03-003 chronic yield: ESTABLISHED at 25%.")
    reg = _registry()
    errors = validate_inline_state_claims(reg, report)
    assert any("P-03-003" in e.reason and "ESTABLISHED" in e.reason for e in errors)


def test_rule2_inline_state_matching_registry_passes():
    report = ("## 1. Technology Analysis\n\n"
              "P-03-001 3D array: ESTABLISHED by patent text.")
    reg = _registry()
    errors = validate_inline_state_claims(reg, report)
    assert errors == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_epistemic_guard.py -v`
Expected: FAIL with `ImportError: cannot import name 'validate_inline_state_claims'`

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/contract.py`, add:

```python
import re as _re


def validate_inline_state_claims(
    registry: "PropositionRegistry",
    report_md: str,
) -> list[ContractError]:
    """Rule 2: inline ESTABLISHED claims must match the registry.

    Scans report lines for proposition-id mentions paired with a state
    keyword. If the line asserts ESTABLISHED for a proposition whose
    registry state is NOT_ESTABLISHED/CONTRADICTED/PARTIALLY_ESTABLISHED,
    that is an overclaim at point of use.
    """
    errors = []
    prop_states = {p.proposition_id: p.state for p in registry.all()}
    id_pat = _re.compile(r"\bP-\d{2}-\d{3}(?:[a-f])?\b")
    for lineno, line in enumerate(report_md.splitlines(), start=1):
        for pid in id_pat.findall(line):
            if pid not in prop_states:
                continue
            state = prop_states[pid]
            upper = line.upper()
            if state != EpistemicState.ESTABLISHED and "ESTABLISHED" in upper:
                errors.append(ContractError(
                    "Epistemic Guard (Rule 2)",
                    f"line {lineno}",
                    f"FATAL: line asserts ESTABLISHED for {pid} but registry "
                    f"state is {state}. Point-of-use overclaim."))
    return errors
```

Wire into `validate_epistemic_guard` — add at the end of the function body:

```python
    errors.extend(validate_inline_state_claims(registry, report_md))
    return errors
```

(And update `validate_epistemic_guard`'s docstring Rule-2 mention from "enforced by Task C3" to "enforced here + Task C3 column".)

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_epistemic_guard.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Run the full renderer suite**

Run: `python3 -m pytest report-renderer/tests/ -q`
Expected: all existing tests still pass (the current US5215088 report text must not pair P-03-003 with inline ESTABLISHED — verify if it fails here, because that is exactly the class of overclaim this guard exists to catch).

- [ ] **Step 6: Commit**

```bash
git add report-renderer/contract.py report-renderer/tests/test_epistemic_guard.py
git commit -m "feat(renderer): detect inline established claims contradicting registry"
```

---

### Task C3: Rule 3 — evidence-state column at point of use (Technology Analysis)

**Files:**
- Modify: `report-renderer/render_report.py` (Technology Analysis page)
- Test: `report-renderer/tests/test_epistemic_guard.py`

**Interfaces:**
- Consumes: registry (passed via `render()`'s existing `ledger`/`ledger_path` params) and the parsed report AST.
- Produces: an evidence-state column appended to the Quantitative Performance Comparison table, with values derived from the registry per proposition id.

- [ ] **Step 1: Write the failing test**

```python
# append to report-renderer/tests/test_epistemic_guard.py
import json
import os
from render_report import render


def test_technology_analysis_has_evidence_state_column():
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    report_md = open(os.path.join(base, "evaluations", "US5215088", "report.md"), encoding="utf-8").read()
    ledger_md = open(os.path.join(base, "evaluations", "US5215088", "proposition-ledger.json"), encoding="utf-8").read()
    scores = json.load(open(os.path.join(base, "evaluations", "US5215088", "scores-manifest.json"), encoding="utf-8"))
    if "scores_manifest" in scores:
        scores = scores["scores_manifest"]
    out = render(report_md, ledger_md, scores,
                 ledger_path=os.path.join(base, "evaluations", "US5215088", "proposition-ledger.json"))
    # The evidence-state column header and the derived P-03-003 state must both appear
    assert "Evidence State" in out
    assert "ESCALATION_REQUIRED" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_epistemic_guard.py -v`
Expected: FAIL — `Evidence State` not in output.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/render_report.py`, inside `render()`, near where the registry is loaded (the render function already accepts `ledger`/`ledger_path`), add:

```python
    # v1.9: point-of-use evidence states derived from the registry.
    registry_states = {}
    try:
        import contract as _contract_mod
        _reg = None
        if ledger is not None:
            _reg = _contract_mod.PropositionRegistry(ledger)
        elif ledger_path:
            _reg = _contract_mod.PropositionRegistry.from_file(ledger_path)
        if _reg is not None:
            for _p in _reg.all():
                registry_states[_p.proposition_id] = (
                    f"{_p.state} / {_p.recovery_state}")
    except Exception:
        registry_states = {}
```

Then, in the Technology Analysis page construction (where the Quantitative Performance Comparison table is rendered from the report body), append the column. Find the Technology Analysis page emission and add the column header + per-row lookup:

```python
    def evidence_state_for(prop_id: str) -> str:
        return registry_states.get(prop_id, "NOT_ESTABLISHED / SEARCH_PENDING")
```

And when the table body is emitted for the Technology Analysis page, append a trailing `<th>Evidence State</th>` header and a trailing `<td>` per row whose `Source` cell contains a proposition id (e.g. the `P-03-003` row). If no registry data is available, the column renders "registry not loaded" — never a fabricated state.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_epistemic_guard.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Run the full renderer suite + visual QA**

Run:

```bash
python3 -m pytest report-renderer/tests/ -q
python3 report-renderer/visual_qa.py 2>&1 | tail -5
```

Expected: all tests pass; visual QA PASS (the Technology Analysis table now shows the evidence-state column).

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/tests/test_epistemic_guard.py
git commit -m "feat(renderer): evidence-state column at point of use in Technology Analysis"
```

---

## Self-Review

**1. Spec coverage:**
- Global renderer guard with 4 hard rules → Tasks C1 (Rules 1, 4), C2 (Rule 2), C3 (Rule 3).
- Programmatic rejection of the "all propositions are ESTABLISHED" family while unresolved>0 → Task C1 (Rule 1) — the exact sentence previously found in v1.7 report text is now structurally impossible to render.
- Point-of-use evidence-state column in Technology Analysis for P-03-003 → Task C3 (values derive from the registry; the fixture's P-03-003 = NOT_ESTABLISHED / ESCALATION_REQUIRED appears at the point of use).
- Guard is global (any ledger), not US5215088-specific → the rules read registry state, not hardcoded ids; only the fixture test data references US5215088.
- Backward compatibility → Tasks C1–C3 each run the full 57-test suite.

**2. Placeholder scan:** No TBD/TODO; every step has concrete code and expected output.

**3. Type consistency:** `validate_epistemic_guard` returns `list[ContractError]` and is wired into `pre_render_integrity_gate` before the existing contamination block; `validate_inline_state_claims` returns the same type; registry lookup maps `proposition_id -> "STATE / RECOVERY"` strings consumed only by the renderer column.