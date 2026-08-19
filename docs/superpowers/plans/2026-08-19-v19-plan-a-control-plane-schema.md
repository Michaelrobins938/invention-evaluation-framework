# Plan A — v1.9 Control-Plane Schema: State Lattice + Scope + Evidence Debt

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the conflated `ResolutionState` into two orthogonal axes — `EpistemicState` (what we know) and `RecoveryState` (what we can still do about it) — add a `Scope` dimension to every proposition, and redefine evidence debt as recoverable-items-only.

**Architecture:** The engine (`engine_v17/models.py`) becomes the canonical home of the lattice. `Proposition` carries `epistemic_state` + `recovery_state` + `scope`; the legacy `state` field becomes a derived compatibility property. The renderer contract (`report-renderer/contract.py`) mirrors the canonical enums so the pre-render gate and the registry speak the same vocabulary. `calculate_evidence_debt` excludes `UNAVAILABLE_BY_CONSTRAINT` and `NONE_REQUIRED` items. A migration path converts existing ledgers (v1.7/v1.8 `status` values) into the lattice.

**Tech Stack:** Python 3.10+ (repo runs 3.14), pytest, dataclasses + `Enum`, JSON ledgers.

## Global Constraints

- Canonical epistemic states: `ESTABLISHED`, `PARTIALLY_ESTABLISHED`, `NOT_ESTABLISHED`, `CONTRADICTED`.
- Canonical recovery states: `NONE_REQUIRED`, `SEARCH_PENDING`, `ESCALATION_REQUIRED`, `EXHAUSTED`, `UNAVAILABLE_BY_CONSTRAINT`.
- Canonical scopes: `TARGET_PATENT`, `PATENT_FAMILY`, `TECHNOLOGY_LINEAGE`, `COMMERCIAL_PRODUCT`, `ASSIGNEE_PORTFOLIO`, `MARKET`, `REGULATORY`.
- Evidence debt = propositions whose recovery state is `SEARCH_PENDING` or `ESCALATION_REQUIRED` (recoverable). `UNAVAILABLE_BY_CONSTRAINT` and `NONE_REQUIRED` are NOT debt.
- US5215088 fixture states (authoritative, from user review): P-03-003 = NOT_ESTABLISHED + ESCALATION_REQUIRED; P-06-005, P-07-001 = PARTIALLY_ESTABLISHED + SEARCH_PENDING; P-08-005 = PARTIALLY_ESTABLISHED + UNAVAILABLE_BY_CONSTRAINT (parent; residual gap is confidential); P-08-005a/b/c = ESTABLISHED + NONE_REQUIRED; P-08-005d/e/f = NOT_ESTABLISHED + UNAVAILABLE_BY_CONSTRAINT.
- Legacy `ResolutionState` mapping: ESTABLISHED→(ESTABLISHED, NONE_REQUIRED); UNRESOLVED→(NOT_ESTABLISHED, SEARCH_PENDING); ESCALATION_REQUIRED→(NOT_ESTABLISHED, ESCALATION_REQUIRED); SEARCH_EXHAUSTED→(NOT_ESTABLISHED, EXHAUSTED); BLOCKED→(NOT_ESTABLISHED, ESCALATION_REQUIRED); MIGRATION_REQUIRED→(NOT_ESTABLISHED, SEARCH_PENDING).
- Backward compatibility: existing engine tests in `Test-report-results/tests_v17/` must keep passing; `transition_state()` keeps its legacy return type as a shim; new canonical function is `transition_lattice()`.
- No report-specific hand-fixes. All changes are engine/renderer-level.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`).

## File Structure

- `engine_v17/models.py` — add `EpistemicState`, `RecoveryState`, `Scope` enums; `LEGACY_STATE_MAP`; `lattice_from_legacy()`; `legacy_from_lattice()`; extend `Proposition` with the three new fields + derived `state` property.
- `engine_v17/recovery.py` — add `transition_lattice()`; make `transition_state()` delegate to it.
- `engine_v17/constraints.py` — `calculate_evidence_debt()` excludes non-recoverable items.
- `engine_v17/migration.py` — `migrate_v18_ledger()` converts ledger dicts to the lattice.
- `report-renderer/contract.py` — replace `EpistemicState` class with canonical enum values (keep legacy aliases); add `RecoveryState` and `Scope`; extend `Proposition` + `PropositionRegistry.load`.
- `Test-report-results/tests_v17/test_lattice.py` — new engine tests.
- `report-renderer/tests/test_lattice_contract.py` — new renderer tests.
- `evaluations/US5215088/proposition-ledger.json` — migrated fixture (via migration script, committed as data).

---

### Task A1: Canonical enums + legacy mapping in `engine_v17/models.py`

**Files:**
- Modify: `engine_v17/models.py` (after `ResolutionState`, before `FailureClass`)
- Test: `Test-report-results/tests_v17/test_lattice.py` (new)

**Interfaces:**
- Consumes: existing `ResolutionState` enum.
- Produces: `EpistemicState`, `RecoveryState`, `Scope` enums; `LEGACY_STATE_MAP: dict[ResolutionState, tuple[EpistemicState, RecoveryState]]`; `lattice_from_legacy(state: ResolutionState) -> tuple[EpistemicState, RecoveryState]`; `legacy_from_lattice(epistemic: EpistemicState, recovery: RecoveryState) -> ResolutionState`.

- [ ] **Step 1: Write the failing test**

```python
# Test-report-results/tests_v17/test_lattice.py
from engine_v17.models import (
    EpistemicState, RecoveryState, Scope, ResolutionState,
    lattice_from_legacy, legacy_from_lattice,
)


def test_legacy_established_maps_to_established_none_required():
    assert lattice_from_legacy(ResolutionState.ESTABLISHED) == (
        EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED)


def test_legacy_escalation_maps_to_not_established_escalation():
    assert lattice_from_legacy(ResolutionState.ESCALATION_REQUIRED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED)


def test_legacy_search_exhausted_maps_to_exhausted():
    assert lattice_from_legacy(ResolutionState.SEARCH_EXHAUSTED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED)


def test_legacy_unresolved_maps_to_search_pending():
    assert lattice_from_legacy(ResolutionState.UNRESOLVED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING)


def test_legacy_blocked_maps_to_escalation():
    assert lattice_from_legacy(ResolutionState.BLOCKED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED)


def test_legacy_migration_required_maps_to_search_pending():
    assert lattice_from_legacy(ResolutionState.MIGRATION_REQUIRED) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING)


def test_round_trip_established():
    assert legacy_from_lattice(EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED) == ResolutionState.ESTABLISHED


def test_round_trip_exhausted():
    assert legacy_from_lattice(EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED) == ResolutionState.SEARCH_EXHAUSTED


def test_scope_enum_has_all_seven_values():
    assert {s.value for s in Scope} == {
        "TARGET_PATENT", "PATENT_FAMILY", "TECHNOLOGY_LINEAGE",
        "COMMERCIAL_PRODUCT", "ASSIGNEE_PORTFOLIO", "MARKET", "REGULATORY",
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: FAIL with `ImportError: cannot import name 'EpistemicState'`

- [ ] **Step 3: Write minimal implementation**

In `engine_v17/models.py`, after the `ResolutionState` enum (line ~28), add:

```python
class EpistemicState(str, Enum):
    """What we know about a proposition. Orthogonal to RecoveryState."""
    ESTABLISHED = "ESTABLISHED"
    PARTIALLY_ESTABLISHED = "PARTIALLY_ESTABLISHED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    CONTRADICTED = "CONTRADICTED"


class RecoveryState(str, Enum):
    """What can still be done about a proposition. Orthogonal to EpistemicState."""
    NONE_REQUIRED = "NONE_REQUIRED"
    SEARCH_PENDING = "SEARCH_PENDING"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    EXHAUSTED = "EXHAUSTED"
    UNAVAILABLE_BY_CONSTRAINT = "UNAVAILABLE_BY_CONSTRAINT"


class Scope(str, Enum):
    """What entity a proposition refers to. Prevents cross-entity contamination
    (e.g. US5215088 claims vs Neuralace claims)."""
    TARGET_PATENT = "TARGET_PATENT"
    PATENT_FAMILY = "PATENT_FAMILY"
    TECHNOLOGY_LINEAGE = "TECHNOLOGY_LINEAGE"
    COMMERCIAL_PRODUCT = "COMMERCIAL_PRODUCT"
    ASSIGNEE_PORTFOLIO = "ASSIGNEE_PORTFOLIO"
    MARKET = "MARKET"
    REGULATORY = "REGULATORY"


# v1.9: legacy single-axis state -> (epistemic, recovery) lattice.
LEGACY_STATE_MAP: dict[ResolutionState, tuple[EpistemicState, RecoveryState]] = {
    ResolutionState.ESTABLISHED: (EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED),
    ResolutionState.UNRESOLVED: (EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING),
    ResolutionState.ESCALATION_REQUIRED: (EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED),
    ResolutionState.SEARCH_EXHAUSTED: (EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED),
    ResolutionState.BLOCKED: (EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED),
    ResolutionState.MIGRATION_REQUIRED: (EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING),
}

# Reverse map for the backward-compat `state` property.
_LATTICE_TO_LEGACY: dict[tuple[EpistemicState, RecoveryState], ResolutionState] = {
    (e, r): s for s, (e, r) in LEGACY_STATE_MAP.items()
}


def lattice_from_legacy(state: ResolutionState) -> tuple[EpistemicState, RecoveryState]:
    return LEGACY_STATE_MAP.get(state, (EpistemicState.NOT_ESTABLISHED, RecoveryState.SEARCH_PENDING))


def legacy_from_lattice(epistemic: EpistemicState, recovery: RecoveryState) -> ResolutionState:
    return _LATTICE_TO_LEGACY.get((epistemic, recovery), ResolutionState.UNRESOLVED)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/models.py Test-report-results/tests_v17/test_lattice.py
git commit -m "feat(engine): add v1.9 epistemic/recovery state lattice and scope enum"
```

---

### Task A2: `Proposition` carries the lattice + scope (backward-compatible)

**Files:**
- Modify: `engine_v17/models.py` (`Proposition` dataclass, `from_dict`, `to_dict`)
- Test: `Test-report-results/tests_v17/test_lattice.py`

**Interfaces:**
- Consumes: `EpistemicState`, `RecoveryState`, `Scope`, `lattice_from_legacy`, `legacy_from_lattice` (Task A1).
- Produces: `Proposition` with fields `epistemic_state: EpistemicState`, `recovery_state: RecoveryState`, `scope: Scope`, and a derived read-only `state` property returning `ResolutionState`. `from_dict` accepts either the new fields or legacy `state`; `to_dict` emits the new fields plus a legacy `state` for compatibility.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_lattice.py
from engine_v17.models import Proposition


def test_proposition_from_legacy_state_migrates_to_lattice():
    p = Proposition.from_dict({"id": "P-07-001", "state": "EXHAUSTED"})
    assert p.epistemic_state == EpistemicState.NOT_ESTABLISHED
    assert p.recovery_state == RecoveryState.EXHAUSTED


def test_proposition_from_new_fields_round_trips():
    p = Proposition.from_dict({
        "id": "P-08-005d",
        "claim": "Confidential royalty rate",
        "epistemic_state": "NOT_ESTABLISHED",
        "recovery_state": "UNAVAILABLE_BY_CONSTRAINT",
        "scope": "COMMERCIAL_PRODUCT",
    })
    assert p.epistemic_state == EpistemicState.NOT_ESTABLISHED
    assert p.recovery_state == RecoveryState.UNAVAILABLE_BY_CONSTRAINT
    assert p.scope == Scope.COMMERCIAL_PRODUCT
    d = p.to_dict()
    assert d["epistemic_state"] == "NOT_ESTABLISHED"
    assert d["recovery_state"] == "UNAVAILABLE_BY_CONSTRAINT"
    assert d["scope"] == "COMMERCIAL_PRODUCT"
    assert d["state"] == "UNRESOLVED"  # legacy shim


def test_proposition_state_property_maps_back():
    p = Proposition(id="P-03-003", claim="x",
                    epistemic_state=EpistemicState.NOT_ESTABLISHED,
                    recovery_state=RecoveryState.ESCALATION_REQUIRED)
    assert p.state == ResolutionState.ESCALATION_REQUIRED


def test_proposition_default_scope_is_target_patent():
    p = Proposition(id="P-03-001", claim="y")
    assert p.scope == Scope.TARGET_PATENT
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: FAIL — `Proposition` has no `epistemic_state` attribute.

- [ ] **Step 3: Write minimal implementation**

Replace the `Proposition` dataclass fields (lines 184-198) with:

```python
@dataclass
class Proposition:
    id: str
    claim: str = ""
    epistemic_state: EpistemicState = EpistemicState.NOT_ESTABLISHED
    recovery_state: RecoveryState = RecoveryState.SEARCH_PENDING
    scope: Scope = Scope.TARGET_PATENT
    evidence_state: EvidenceState = EvidenceState.WORK_QUEUE
    unknown_type: UnknownType | None = None
    search_completeness: str = "incomplete"
    evidence_strength: str = "insufficient"
    confidence: str = "low"
    blockers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    downstream_effects: list[str] = field(default_factory=list)
    recovery: ResearchExhaustion | None = None
    evidence_sufficiency_passed: bool = False
    migration_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def state(self) -> ResolutionState:
        """Backward-compat: map the lattice back to the legacy single axis."""
        return legacy_from_lattice(self.epistemic_state, self.recovery_state)
```

Update `from_dict` (lines 200-226) to:

```python
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Proposition":
        raw_state = str(data.get("state", ResolutionState.UNRESOLVED.value)).lower()
        if raw_state == "exhausted":
            legacy = ResolutionState.MIGRATION_REQUIRED
            migration = dict(data.get("migration_metadata", {}))
            migration["legacy_state"] = "EXHAUSTED"
        else:
            legacy = _resolution(raw_state) or ResolutionState.UNRESOLVED
            migration = dict(data.get("migration_metadata", {}))
        if "epistemic_state" in data or "recovery_state" in data:
            epistemic = _epistemic(data.get("epistemic_state")) or EpistemicState.NOT_ESTABLISHED
            recovery = _recovery(data.get("recovery_state")) or RecoveryState.SEARCH_PENDING
        else:
            epistemic, recovery = lattice_from_legacy(legacy)
        raw_unknown = data.get("unknown_type")
        return cls(
            id=data["id"],
            claim=data.get("claim", ""),
            epistemic_state=epistemic,
            recovery_state=recovery,
            scope=_scope(data.get("scope")) or Scope.TARGET_PATENT,
            evidence_state=_evidence(data.get("evidence_state")),
            unknown_type=_unknown(raw_unknown),
            search_completeness=data.get("search_completeness", "incomplete"),
            evidence_strength=data.get("evidence_strength", "insufficient"),
            confidence=data.get("confidence", "low"),
            blockers=list(data.get("blockers", [])),
            dependencies=list(data.get("dependencies", [])),
            downstream_effects=list(data.get("downstream_effects", [])),
            recovery=ResearchExhaustion.from_dict(data["recovery"]) if data.get("recovery") else None,
            evidence_sufficiency_passed=bool(data.get("evidence_sufficiency_passed", False)),
            migration_metadata=migration,
        )
```

Update `to_dict` (lines 228-246) to:

```python
    def to_dict(self) -> dict[str, Any]:
        result = {
            "id": self.id,
            "claim": self.claim,
            "state": self.state.value,  # legacy shim
            "epistemic_state": self.epistemic_state.value,
            "recovery_state": self.recovery_state.value,
            "scope": self.scope.value,
            "evidence_state": self.evidence_state.value,
            "unknown_type": self.unknown_type.value if self.unknown_type else None,
            "search_completeness": self.search_completeness,
            "evidence_strength": self.evidence_strength,
            "confidence": self.confidence,
            "blockers": self.blockers,
            "dependencies": self.dependencies,
            "downstream_effects": self.downstream_effects,
            "evidence_sufficiency_passed": self.evidence_sufficiency_passed,
            "migration_metadata": self.migration_metadata,
        }
        if self.recovery:
            result["recovery"] = self.recovery.to_dict()
        return result
```

Add the three parser helpers at the bottom of `models.py` (next to `_resolution`):

```python
def _epistemic(value: Any) -> EpistemicState | None:
    if value is None:
        return None
    try:
        return EpistemicState(str(value).upper())
    except ValueError:
        return None


def _recovery(value: Any) -> RecoveryState | None:
    if value is None:
        return None
    try:
        return RecoveryState(str(value).upper())
    except ValueError:
        return None


def _scope(value: Any) -> Scope | None:
    if value is None:
        return None
    try:
        return Scope(str(value).upper())
    except ValueError:
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: PASS (13 passed)

- [ ] **Step 5: Run the full engine suite to confirm backward compatibility**

Run: `python3 -m pytest Test-report-results/tests_v17/ -q`
Expected: all existing tests still pass (the `state` property preserves legacy behavior).

- [ ] **Step 6: Commit**

```bash
git add engine_v17/models.py Test-report-results/tests_v17/test_lattice.py
git commit -m "feat(engine): Proposition carries epistemic/recovery lattice and scope"
```

---

### Task A3: `transition_lattice()` in `engine_v17/recovery.py`

**Files:**
- Modify: `engine_v17/recovery.py` (`transition_state` → delegate; add `transition_lattice`)
- Test: `Test-report-results/tests_v17/test_lattice.py`

**Interfaces:**
- Consumes: `EpistemicState`, `RecoveryState`, `lattice_from_legacy`, `legacy_from_lattice` (Task A1); existing `transition_state` logic.
- Produces: `transition_lattice(proposition, attempts, execution_ledger=None) -> tuple[EpistemicState, RecoveryState]`; `transition_state` keeps its `ResolutionState` return type by delegating.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_lattice.py
from engine_v17.recovery import transition_lattice, RecoveryAttempt
from engine_v17.execution import ExecutionLedger


def test_transition_lattice_no_attempts_is_escalation():
    p = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    assert transition_lattice(p, []) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.ESCALATION_REQUIRED)


def test_transition_lattice_evidence_passed_is_established():
    p = Proposition(id="P-03-001", claim="3D array", evidence_sufficiency_passed=True)
    attempts = [RecoveryAttempt("primary_patent_database", "keyword", result_count=3)]
    assert transition_lattice(p, attempts) == (
        EpistemicState.ESTABLISHED, RecoveryState.NONE_REQUIRED)


def test_transition_lattice_terminal_exhaustion():
    p = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    ledger = ExecutionLedger(run_id="RUN-05")
    attempts = [
        RecoveryAttempt("primary_patent_database", "keyword", result_count=0, strategy_class="terminology"),
        RecoveryAttempt("primary_patent_database", "verified_classification", result_count=0, strategy_class="classification"),
        RecoveryAttempt("primary_patent_database", "citation_traversal", result_count=0, strategy_class="citation_lineage"),
        RecoveryAttempt("primary_patent_database", "family_traversal", result_count=0, strategy_class="family"),
        RecoveryAttempt("secondary_patent_database", "keyword", result_count=0, strategy_class="terminology"),
        RecoveryAttempt("secondary_patent_database", "verified_classification", result_count=0, strategy_class="classification"),
        RecoveryAttempt("secondary_patent_database", "citation_traversal", result_count=0, strategy_class="citation_lineage"),
        RecoveryAttempt("secondary_patent_database", "family_traversal", result_count=0, strategy_class="family"),
    ]
    for a in attempts:
        a.execution_id = ledger.record(a)
    assert transition_lattice(p, attempts, ledger) == (
        EpistemicState.NOT_ESTABLISHED, RecoveryState.EXHAUSTED)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: FAIL with `ImportError: cannot import name 'transition_lattice'`

- [ ] **Step 3: Write minimal implementation**

In `engine_v17/recovery.py`, add `transition_lattice` above `transition_state` and make `transition_state` delegate:

```python
def transition_lattice(
    proposition: Proposition,
    attempts: list[RecoveryAttempt],
    execution_ledger: ExecutionLedger | None = None,
) -> tuple[EpistemicState, RecoveryState]:
    """v1.9 canonical transition: returns (epistemic, recovery) separately.

    The legacy single-axis state conflated 'what we know' with 'what we can
    still do'. This function keeps the two axes distinct:
      - epistemic: ESTABLISHED / PARTIALLY_ESTABLISHED / NOT_ESTABLISHED / CONTRADICTED
      - recovery:  NONE_REQUIRED / SEARCH_PENDING / ESCALATION_REQUIRED / EXHAUSTED / UNAVAILABLE_BY_CONSTRAINT
    """
    legacy = transition_state(proposition, attempts, execution_ledger)
    return lattice_from_legacy(legacy)


def transition_state(
    proposition: Proposition,
    attempts: list[RecoveryAttempt],
    execution_ledger: ExecutionLedger | None = None,
) -> ResolutionState:
    # ... existing body unchanged (lines 195-262) ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: PASS (16 passed)

- [ ] **Step 5: Run the full engine suite**

Run: `python3 -m pytest Test-report-results/tests_v17/ -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add engine_v17/recovery.py Test-report-results/tests_v17/test_lattice.py
git commit -m "feat(engine): add transition_lattice returning separate epistemic/recovery axes"
```

---

### Task A4: Evidence debt = recoverable items only

**Files:**
- Modify: `engine_v17/constraints.py` (`calculate_evidence_debt`)
- Test: `Test-report-results/tests_v17/test_lattice.py`

**Interfaces:**
- Consumes: `Proposition` lattice fields (Task A2).
- Produces: `calculate_evidence_debt(propositions) -> list[EvidenceDebtItem]` that excludes `ESTABLISHED`/`NONE_REQUIRED` and `UNAVAILABLE_BY_CONSTRAINT` propositions.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_lattice.py
from engine_v17.constraints import calculate_evidence_debt


def test_evidence_debt_excludes_unavailable_by_constraint():
    props = [
        Proposition(id="P-08-005d", claim="royalty",
                    epistemic_state=EpistemicState.NOT_ESTABLISHED,
                    recovery_state=RecoveryState.UNAVAILABLE_BY_CONSTRAINT),
        Proposition(id="P-03-003", claim="yield",
                    epistemic_state=EpistemicState.NOT_ESTABLISHED,
                    recovery_state=RecoveryState.ESCALATION_REQUIRED),
        Proposition(id="P-03-001", claim="3D array",
                    epistemic_state=EpistemicState.ESTABLISHED,
                    recovery_state=RecoveryState.NONE_REQUIRED),
    ]
    debt = calculate_evidence_debt(props)
    ids = {d.proposition_id for d in debt}
    assert ids == {"P-03-003"}


def test_evidence_debt_includes_search_pending():
    props = [
        Proposition(id="P-06-005", claim="market share",
                    epistemic_state=EpistemicState.PARTIALLY_ESTABLISHED,
                    recovery_state=RecoveryState.SEARCH_PENDING),
    ]
    debt = calculate_evidence_debt(props)
    assert [d.proposition_id for d in debt] == ["P-06-005"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: FAIL — `P-08-005d` currently appears in debt.

- [ ] **Step 3: Write minimal implementation**

Replace `calculate_evidence_debt` in `engine_v17/constraints.py`:

```python
def calculate_evidence_debt(propositions: list[Proposition]) -> list[EvidenceDebtItem]:
    """Evidence debt = recoverable gaps only.

    v1.9: a proposition is debt iff its recovery state is SEARCH_PENDING or
    ESCALATION_REQUIRED. ESTABLISHED (NONE_REQUIRED) and
    UNAVAILABLE_BY_CONSTRAINT propositions are NOT debt — the latter cannot
    be recovered by any admissible search and must not be counted as if they
    could.
    """
    items = []
    for p in propositions:
        if p.recovery_state in (RecoveryState.NONE_REQUIRED, RecoveryState.UNAVAILABLE_BY_CONSTRAINT):
            continue
        score = 100 if any(t in p.id for t in ("P-05", "P-02")) else 60
        items.append(EvidenceDebtItem(
            proposition_id=p.id,
            severity="high" if score >= 80 else "medium",
            impact=list(p.downstream_effects),
            next_action="execute recovery policy and attach exhaustion proof",
            score=score,
        ))
    return sorted(items, key=lambda item: (-item.score, item.proposition_id))
```

Add the import at the top of `constraints.py`:

```python
from .models import Proposition, RecoveryState, ResolutionState
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: PASS (18 passed)

- [ ] **Step 5: Run the full engine suite**

Run: `python3 -m pytest Test-report-results/tests_v17/ -q`
Expected: all pass (existing `test_constraints.py` uses legacy `state`; the `state` property still maps `ESCALATION_REQUIRED` correctly).

- [ ] **Step 6: Commit**

```bash
git add engine_v17/constraints.py Test-report-results/tests_v17/test_lattice.py
git commit -m "feat(engine): evidence debt counts recoverable items only"
```

---

### Task A5: Renderer contract mirrors the canonical lattice

**Files:**
- Modify: `report-renderer/contract.py` (`EpistemicState` class → canonical values; add `RecoveryState`, `Scope`; extend `Proposition`, `PropositionRegistry.load`)
- Test: `report-renderer/tests/test_lattice_contract.py` (new)

**Interfaces:**
- Consumes: nothing new (standalone module).
- Produces: `EpistemicState` with canonical values + legacy aliases (`PARTIAL`→`PARTIALLY_ESTABLISHED`, `INFERRED`/`NOT_LOADED`/`UNKNOWN`→`NOT_ESTABLISHED`); `RecoveryState`; `Scope`; `Proposition` with `scope` + `recovery_state`; `PropositionRegistry.load` reading new fields with legacy fallback.

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_lattice_contract.py
import json
import pytest
from contract import (
    EpistemicState, RecoveryState, Scope, PropositionRegistry,
)


def test_epistemic_state_has_canonical_values():
    assert EpistemicState.ESTABLISHED == "ESTABLISHED"
    assert EpistemicState.PARTIALLY_ESTABLISHED == "PARTIALLY_ESTABLISHED"
    assert EpistemicState.NOT_ESTABLISHED == "NOT_ESTABLISHED"
    assert EpistemicState.CONTRADICTED == "CONTRADICTED"


def test_legacy_partial_aliases_to_partially_established():
    assert EpistemicState.PARTIAL == EpistemicState.PARTIALLY_ESTABLISHED


def test_recovery_state_values():
    assert {r for r in RecoveryState} == {
        "NONE_REQUIRED", "SEARCH_PENDING", "ESCALATION_REQUIRED",
        "EXHAUSTED", "UNAVAILABLE_BY_CONSTRAINT",
    }


def test_scope_values():
    assert {s for s in Scope} == {
        "TARGET_PATENT", "PATENT_FAMILY", "TECHNOLOGY_LINEAGE",
        "COMMERCIAL_PRODUCT", "ASSIGNEE_PORTFOLIO", "MARKET", "REGULATORY",
    }


def test_registry_loads_new_lattice_fields():
    ledger = {"proposition_ledger": {
        "P-08-005d": {
            "claim": "Confidential royalty rate",
            "epistemic_state": "NOT_ESTABLISHED",
            "recovery_state": "UNAVAILABLE_BY_CONSTRAINT",
            "scope": "COMMERCIAL_PRODUCT",
        },
    }}
    reg = PropositionRegistry(ledger)
    prop = reg.get("P-08-005d")
    assert prop.state == "NOT_ESTABLISHED"
    assert prop.recovery_state == "UNAVAILABLE_BY_CONSTRAINT"
    assert prop.scope == "COMMERCIAL_PRODUCT"


def test_registry_migrates_legacy_status():
    ledger = {"proposition_ledger": {
        "P-03-003": {"claim": "yield", "status": "ESCALATION_REQUIRED"},
    }}
    reg = PropositionRegistry(ledger)
    prop = reg.get("P-03-003")
    assert prop.state == "NOT_ESTABLISHED"
    assert prop.recovery_state == "ESCALATION_REQUIRED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_lattice_contract.py -v`
Expected: FAIL — `EpistemicState.PARTIALLY_ESTABLISHED` missing.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/contract.py`, replace the `EpistemicState` class (lines 227-246) with:

```python
class EpistemicState:
    """Canonical v1.9 epistemic states (what we know)."""
    ESTABLISHED = "ESTABLISHED"
    PARTIALLY_ESTABLISHED = "PARTIALLY_ESTABLISHED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    CONTRADICTED = "CONTRADICTED"

    # Legacy aliases (v1.7/v1.8 vocabulary) — kept so old ledgers and
    # report text still validate.
    PARTIAL = PARTIALLY_ESTABLISHED
    INFERRED = NOT_ESTABLISHED
    NOT_LOADED = NOT_ESTABLISHED
    UNKNOWN = NOT_ESTABLISHED

    # Confidence levels (unchanged)
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"

    # Source types (unchanged)
    DIRECT_EVIDENCE = "DIRECT_EVIDENCE"
    DERIVED = "DERIVED"
    BENCHMARK = "BENCHMARK"
    ASSUMPTION = "ASSUMPTION"


class RecoveryState:
    """Canonical v1.9 recovery states (what can still be done)."""
    NONE_REQUIRED = "NONE_REQUIRED"
    SEARCH_PENDING = "SEARCH_PENDING"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    EXHAUSTED = "EXHAUSTED"
    UNAVAILABLE_BY_CONSTRAINT = "UNAVAILABLE_BY_CONSTRAINT"


class Scope:
    """What entity a proposition refers to."""
    TARGET_PATENT = "TARGET_PATENT"
    PATENT_FAMILY = "PATENT_FAMILY"
    TECHNOLOGY_LINEAGE = "TECHNOLOGY_LINEAGE"
    COMMERCIAL_PRODUCT = "COMMERCIAL_PRODUCT"
    ASSIGNEE_PORTFOLIO = "ASSIGNEE_PORTFOLIO"
    MARKET = "MARKET"
    REGULATORY = "REGULATORY"
```

Extend the `Proposition` dataclass (lines 279-297) with:

```python
@dataclass(frozen=True)
class Proposition:
    """One proposition in the authoritative registry."""
    proposition_id: str
    claim: str
    state: str
    phase: str = ""
    version: str = "v2"
    evidence: tuple = ()
    children: tuple = ()                # atomic decomposition (e.g. P-08-005a..f)
    debt: tuple = ()                    # EvidenceDebt records
    recovery_state: str = RecoveryState.NONE_REQUIRED
    scope: str = Scope.TARGET_PATENT

    @property
    def is_established(self) -> bool:
        return self.state == EpistemicState.ESTABLISHED

    @property
    def is_atomic(self) -> bool:
        return bool(self.children)

    @property
    def is_recoverable_debt(self) -> bool:
        return self.recovery_state in (RecoveryState.SEARCH_PENDING, RecoveryState.ESCALATION_REQUIRED)
```

Update `PropositionRegistry.load` (lines 316-342) to read the new fields with legacy fallback:

```python
    def load(self, ledger: dict) -> None:
        raw = ledger.get("proposition_ledger", ledger)
        for pid, entry in raw.items():
            children = tuple(entry.get("children", ()))
            debt = tuple(
                EvidenceDebt(
                    debt_id=d.get("debt_id", f"{pid}-debt-{i}"),
                    proposition=d.get("proposition", pid),
                    missingness=d.get("missingness", d.get("description", "")),
                    recovery_class=d.get("recovery_class", RecoveryClass.RECOVERY_REQUIRED),
                    severity=d.get("severity", "MODERATE"),
                    recoverable=d.get("recoverable", True),
                    reason=d.get("reason", ""),
                    recommended_action=d.get("recommended_action", ""),
                )
                for i, d in enumerate(entry.get("debt", ()))
            )
            raw_state = entry.get("status", entry.get("state", EpistemicState.UNKNOWN))
            if "epistemic_state" in entry:
                state = entry["epistemic_state"]
            else:
                state = _canonical_state(raw_state)
            self._props[pid] = Proposition(
                proposition_id=pid,
                claim=entry.get("claim", ""),
                state=state,
                phase=entry.get("phase", ""),
                version=entry.get("version", "v2"),
                evidence=tuple(entry.get("evidence", ())),
                children=children,
                debt=debt,
                recovery_state=entry.get("recovery_state", RecoveryState.NONE_REQUIRED),
                scope=entry.get("scope", Scope.TARGET_PATENT),
            )
```

Add the helper at the bottom of `contract.py`:

```python
def _canonical_state(raw: str) -> str:
    """Map legacy state vocabulary to canonical epistemic states."""
    upper = str(raw).upper()
    if upper in ("ESTABLISHED",):
        return EpistemicState.ESTABLISHED
    if upper in ("PARTIALLY_ESTABLISHED", "PARTIAL"):
        return EpistemicState.PARTIALLY_ESTABLISHED
    if upper in ("CONTRADICTED",):
        return EpistemicState.CONTRADICTED
    return EpistemicState.NOT_ESTABLISHED
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_lattice_contract.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Run the full renderer suite**

Run: `python3 -m pytest report-renderer/tests/ -q`
Expected: all 57 existing tests still pass (legacy aliases preserve behavior).

- [ ] **Step 6: Commit**

```bash
git add report-renderer/contract.py report-renderer/tests/test_lattice_contract.py
git commit -m "feat(renderer): mirror canonical epistemic/recovery lattice and scope in contract"
```

---

### Task A6: Migrate the US5215088 ledger + full verification

**Files:**
- Modify: `evaluations/US5215088/proposition-ledger.json` (data migration)
- Modify: `engine_v17/migration.py` (add `migrate_v18_ledger`)
- Test: `Test-report-results/tests_v17/test_lattice.py`

**Interfaces:**
- Consumes: `lattice_from_legacy` (Task A1).
- Produces: `migrate_v18_ledger(ledger: dict) -> dict` that adds `epistemic_state`, `recovery_state`, `scope` to every entry while keeping `status` for compatibility.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_lattice.py
from engine_v17.migration import migrate_v18_ledger


def test_migrate_v18_ledger_adds_lattice_fields():
    ledger = {"proposition_ledger": {
        "P-03-003": {"claim": "yield", "status": "ESCALATION_REQUIRED"},
        "P-08-005d": {"claim": "royalty", "status": "NOT_ESTABLISHED",
                      "recovery_state": "UNAVAILABLE_BY_CONSTRAINT"},
    }}
    out = migrate_v18_ledger(ledger)
    p3 = out["proposition_ledger"]["P-03-003"]
    assert p3["epistemic_state"] == "NOT_ESTABLISHED"
    assert p3["recovery_state"] == "ESCALATION_REQUIRED"
    assert p3["scope"] == "TARGET_PATENT"
    assert p3["status"] == "ESCALATION_REQUIRED"  # legacy kept
    d = out["proposition_ledger"]["P-08-005d"]
    assert d["recovery_state"] == "UNAVAILABLE_BY_CONSTRAINT"
    assert d["epistemic_state"] == "NOT_ESTABLISHED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: FAIL with `ImportError: cannot import name 'migrate_v18_ledger'`

- [ ] **Step 3: Write minimal implementation**

Replace `engine_v17/migration.py`:

```python
"""Migration helpers for v1.6 artifacts and v1.8 -> v1.9 ledgers."""

from .models import (
    EpistemicState, Proposition, RecoveryState, Scope,
    ResolutionState, lattice_from_legacy,
)


def migrate_v16_artifact(data: dict) -> Proposition:
    return Proposition.from_dict(data)


def migrate_v18_ledger(ledger: dict) -> dict:
    """Add v1.9 lattice fields to every proposition entry.

    Keeps the legacy ``status`` key so v1.8 consumers still work. Entries
    that already carry ``epistemic_state``/``recovery_state`` are left
    untouched; only missing fields are filled from the legacy state.
    """
    raw = ledger.get("proposition_ledger", ledger)
    out = dict(ledger)
    migrated = {}
    for pid, entry in raw.items():
        e = dict(entry)
        if "epistemic_state" not in e:
            legacy = ResolutionState(str(e.get("status", e.get("state", "UNRESOLVED"))).upper())
            epi, rec = lattice_from_legacy(legacy)
            e["epistemic_state"] = epi.value
            e["recovery_state"] = e.get("recovery_state", rec.value)
        e.setdefault("recovery_state", RecoveryState.NONE_REQUIRED.value)
        e.setdefault("scope", Scope.TARGET_PATENT.value)
        migrated[pid] = e
    out["proposition_ledger"] = migrated
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_lattice.py -v`
Expected: PASS (19 passed)

- [ ] **Step 5: Migrate the fixture ledger**

Run:

```bash
python3 - <<'EOF'
import json
from engine_v17.migration import migrate_v18_ledger
path = "evaluations/US5215088/proposition-ledger.json"
ledger = json.load(open(path, encoding="utf-8"))
out = migrate_v18_ledger(ledger)
json.dump(out, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("migrated", len(out["proposition_ledger"]), "propositions")
EOF
```

Then apply the authoritative fixture states (from Global Constraints) by editing the migrated JSON:

```bash
python3 - <<'EOF'
import json
path = "evaluations/US5215088/proposition-ledger.json"
ledger = json.load(open(path, encoding="utf-8"))
pl = ledger["proposition_ledger"]
# Authoritative v1.9 states from user review
pl["P-03-003"]["epistemic_state"] = "NOT_ESTABLISHED"
pl["P-03-003"]["recovery_state"] = "ESCALATION_REQUIRED"
pl["P-06-005"]["epistemic_state"] = "PARTIALLY_ESTABLISHED"
pl["P-06-005"]["recovery_state"] = "SEARCH_PENDING"
pl["P-07-001"]["epistemic_state"] = "PARTIALLY_ESTABLISHED"
pl["P-07-001"]["recovery_state"] = "SEARCH_PENDING"
pl["P-08-005"]["epistemic_state"] = "PARTIALLY_ESTABLISHED"
pl["P-08-005"]["recovery_state"] = "UNAVAILABLE_BY_CONSTRAINT"
for child in ("P-08-005a", "P-08-005b", "P-08-005c"):
    pl[child]["epistemic_state"] = "ESTABLISHED"
    pl[child]["recovery_state"] = "NONE_REQUIRED"
for child in ("P-08-005d", "P-08-005e", "P-08-005f"):
    pl[child]["epistemic_state"] = "NOT_ESTABLISHED"
    pl[child]["recovery_state"] = "UNAVAILABLE_BY_CONSTRAINT"
json.dump(ledger, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("fixture states applied")
EOF
```

- [ ] **Step 6: Verify the migrated ledger loads and the registry reports correct debt**

Run:

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, "report-renderer")
from contract import PropositionRegistry, RecoveryState
reg = PropositionRegistry.from_file("evaluations/US5215088/proposition-ledger.json")
unest = reg.unestablished_top_level()
print("unestablished top-level:", [p.proposition_id for p in unest])
debt = [p for p in reg.all() if p.is_recoverable_debt]
print("recoverable debt:", sorted(p.proposition_id for p in debt))
assert sorted(p.proposition_id for p in debt) == ["P-03-003", "P-06-005", "P-07-001"]
print("OK: debt = 3 recoverable items; P-08-005 excluded (UNAVAILABLE_BY_CONSTRAINT)")
EOF
```

Expected: `unestablished top-level: ['P-03-003', 'P-06-005', 'P-07-001', 'P-08-005']` and `recoverable debt: ['P-03-003', 'P-06-005', 'P-07-001']`.

- [ ] **Step 7: Run both full suites**

Run: `python3 -m pytest Test-report-results/tests_v17/ report-renderer/tests/ -q`
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add engine_v17/migration.py evaluations/US5215088/proposition-ledger.json Test-report-results/tests_v17/test_lattice.py
git commit -m "feat(engine): migrate US5215088 ledger to v1.9 lattice with authoritative states"
```

---

## Self-Review

**1. Spec coverage:**
- State lattice split (epistemic × recovery) → Tasks A1, A3, A5.
- CONTRADICTED / PARTIALLY_ESTABLISHED / NOT_ESTABLISHED / NONE_REQUIRED / SEARCH_PENDING / UNAVAILABLE_BY_CONSTRAINT → Tasks A1, A5.
- Scope dimension → Tasks A1, A2, A5.
- Evidence debt ≠ epistemic state (recoverable only) → Task A4.
- UNAVAILABLE_BY_CONSTRAINT promoted to core architecture → Tasks A1, A4, A6.
- Migration path for existing ledgers → Tasks A2, A6.
- Backward compatibility with 18 engine test files → Tasks A2, A3 (shim `state` property, `transition_state` delegate).

**2. Placeholder scan:** No TBD/TODO; every step has concrete code and expected output.

**3. Type consistency:** `transition_lattice` returns `tuple[EpistemicState, RecoveryState]` everywhere; `Proposition.recovery_state` is `RecoveryState` in engine and `str` in renderer contract (renderer uses string constants, matching existing `state: str` pattern); `migrate_v18_ledger` output keys match `PropositionRegistry.load` expectations (`epistemic_state`, `recovery_state`, `scope`).