# Plan E — v1.9 Regulatory Ontology: Typed FDA Status Instead of Prose

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace free-text FDA statements (e.g. "Breakthrough Device Designation: Received for BCI applications") with a typed, machine-verifiable `RegulatoryState` ontology so the renderer can never print "approval" for a clearance, "breakthrough" without a designation record, or a PMA pathway for a device that only holds 510(k) clearance. The ontology lives in `engine_v17/regulatory.py`; the US5215088 facts live in a committed `regulatory_state.yaml` fixture.

**Architecture:** A new engine module `engine_v17/regulatory.py` defines the ontology — `RegulatoryState` (jurisdiction, device, classification, marketing_authorization, clinical_investigation, breakthrough_designation, therapeutic_indication, chronic_use), `build_regulatory_state(records)`, `validate_regulatory_state(state)` (raises on internal contradiction, e.g. breakthrough=true without a designation record), and `regulatory_to_manifest(state)`. The US5215088 fixture is a YAML file (PyYAML 6.0.3 available in-repo). The renderer's `regulatory_table` renders from the ontology and its "Regulatory Burden" rationale is recomputed from the ontology fields rather than hand-written prose.

**Tech Stack:** Python 3.10+ (repo runs 3.14), pytest, dataclasses, PyYAML 6.0.3, JSON manifest.

## Global Constraints

- Canonical `MarketingAuthorization` values: `NONE`, `510K_CLEARANCE`, `PMA_APPROVED`, `HDE_APPROVED`, `NOT_APPLICABLE`, `UNKNOWN`.
- Canonical `ClinicalInvestigation` values: `NONE`, `IDE_GRANTED`, `UNDER_IDE`, `NOT_APPLICABLE`, `UNKNOWN`.
- The word "approval" MUST NOT render for a `510K_CLEARANCE` authorization. The word "breakthrough" MUST NOT render unless `breakthrough_designation=true` AND a designation record exists.
- US5215088 fixture facts (authoritative, from user review): FDA K110010 = 510(k) clearance (NOT approval); NO IDE established; NO breakthrough designation; device = NeuroPort System / Utah Array; classification = Class III (21 CFR 882.8955); chronic human implantation NOT established as a cleared/approved indication (occurs only under research protocols). `chronic_use = NOT_ESTABLISHED`.
- `validate_regulatory_state` MUST reject: `marketing_authorization=510K_CLEARANCE` paired with prose "FDA-approved"; `breakthrough_designation=true` with no `breakthrough_record`; `clinical_investigation=IDE_GRANTED` with no `ide_number`.
- Backward compatibility: the existing `regulatory_resources` block in the manifest stays; the ontology is additive. All existing engine tests (18 files) and renderer tests (57) keep passing.
- No report-specific hand-fixes. All changes are engine/renderer-level; the fixture is data.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`).

## File Structure

- `engine_v17/regulatory.py` — new: `MarketingAuthorization`, `ClinicalInvestigation` constants, `RegulatoryState`, `build_regulatory_state()`, `validate_regulatory_state()`, `regulatory_to_manifest()`, `load_regulatory_yaml()`.
- `evaluations/US5215088/regulatory_state.yaml` — committed fixture ontology.
- `report-renderer/render_report.py` — `regulatory_table` renders from the ontology; `_default_regulatory_resources` in the orchestrator is not modified.
- `Test-report-results/tests_v17/test_regulatory.py` — new engine tests.
- `report-renderer/tests/test_regulatory_render.py` — new renderer tests.

---

### Task E1: Regulatory ontology in `engine_v17/regulatory.py`

**Files:**
- Create: `engine_v17/regulatory.py`
- Test: `Test-report-results/tests_v17/test_regulatory.py` (new)

**Interfaces:**
- Consumes: nothing (standalone module).
- Produces: `RegulatoryState` dataclass (fields below), `build_regulatory_state(records)`, `validate_regulatory_state(state) -> list[str]` (empty = valid), `regulatory_to_manifest(state) -> dict`.

- [ ] **Step 1: Write the failing test**

```python
# Test-report-results/tests_v17/test_regulatory.py
from engine_v17.regulatory import (
    RegulatoryState, build_regulatory_state, validate_regulatory_state,
    regulatory_to_manifest,
)


def test_regulatory_state_round_trip():
    st = RegulatoryState(
        jurisdiction="United States",
        device="NeuroPort System / Utah Array",
        classification="Class III; 21 CFR 882.8955",
        marketing_authorization="510K_CLEARANCE",
        authorization_number="K110010",
        clinical_investigation="NONE",
        breakthrough_designation=False,
        breakthrough_record=None,
        therapeutic_indication="Short-term intracortical monitoring (research use)",
        chronic_use="NOT_ESTABLISHED",
    )
    d = regulatory_to_manifest(st)
    assert d["marketing_authorization"] == "510K_CLEARANCE"
    assert d["authorization_number"] == "K110010"
    assert d["chronic_use"] == "NOT_ESTABLISHED"
    assert validate_regulatory_state(st) == []


def test_regulatory_state_rejects_approval_for_clearance():
    st = RegulatoryState(
        jurisdiction="United States",
        device="NeuroPort System",
        classification="Class III",
        marketing_authorization="510K_CLEARANCE",
        authorization_number="K110010",
        clinical_investigation="NONE",
        breakthrough_designation=False,
        breakthrough_record=None,
        therapeutic_indication="Short-term intracortical monitoring",
        chronic_use="NOT_ESTABLISHED",
    )
    errors = validate_regulatory_state(st)
    assert any("approval" in e.lower() for e in errors)


def test_regulatory_state_rejects_breakthrough_without_record():
    st = RegulatoryState(
        jurisdiction="United States",
        device="NeuroPort System",
        classification="Class III",
        marketing_authorization="510K_CLEARANCE",
        authorization_number="K110010",
        clinical_investigation="NONE",
        breakthrough_designation=True,      # <-- no record
        breakthrough_record=None,
        therapeutic_indication="Short-term intracortical monitoring",
        chronic_use="NOT_ESTABLISHED",
    )
    errors = validate_regulatory_state(st)
    assert any("breakthrough" in e.lower() for e in errors)


def test_regulatory_state_rejects_ide_without_number():
    st = RegulatoryState(
        jurisdiction="United States",
        device="NeuroPort System",
        classification="Class III",
        marketing_authorization="510K_CLEARANCE",
        authorization_number="K110010",
        clinical_investigation="IDE_GRANTED",   # <-- no ide_number
        breakthrough_designation=False,
        breakthrough_record=None,
        therapeutic_indication="Short-term intracortical monitoring",
        chronic_use="NOT_ESTABLISHED",
    )
    errors = validate_regulatory_state(st)
    assert any("ide" in e.lower() for e in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_regulatory.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine_v17.regulatory'`

- [ ] **Step 3: Write minimal implementation**

Create `engine_v17/regulatory.py`:

```python
"""v1.9 regulatory ontology.

Typed FDA/regulatory status so the renderer can never print "approval"
for a clearance, "breakthrough" without a designation record, or a PMA
pathway for a device that only holds 510(k) clearance.

Canonical values (strings, matching the renderer's constant style):
  marketing_authorization: NONE | 510K_CLEARANCE | PMA_APPROVED | HDE_APPROVED
                           | NOT_APPLICABLE | UNKNOWN
  clinical_investigation:  NONE | IDE_GRANTED | UNDER_IDE
                           | NOT_APPLICABLE | UNKNOWN
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class MarketingAuthorization:
    NONE = "NONE"
    CLEARANCE_510K = "510K_CLEARANCE"
    PMA_APPROVED = "PMA_APPROVED"
    HDE_APPROVED = "HDE_APPROVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class ClinicalInvestigation:
    NONE = "NONE"
    IDE_GRANTED = "IDE_GRANTED"
    UNDER_IDE = "UNDER_IDE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class RegulatoryState:
    jurisdiction: str = ""
    device: str = ""
    classification: str = ""
    marketing_authorization: str = MarketingAuthorization.UNKNOWN
    authorization_number: str = ""
    clinical_investigation: str = ClinicalInvestigation.UNKNOWN
    ide_number: str = ""
    breakthrough_designation: bool = False
    breakthrough_record: str | None = None
    therapeutic_indication: str = ""
    chronic_use: str = "NOT_ESTABLISHED"   # NOT_ESTABLISHED | ESTABLISHED | NOT_PERMITTED


def build_regulatory_state(records: list[dict[str, Any]]) -> RegulatoryState:
    """Build a RegulatoryState from YAML/JSON record dicts."""
    first = records[0] if records else {}
    return RegulatoryState(
        jurisdiction=first.get("jurisdiction", ""),
        device=first.get("device", ""),
        classification=first.get("classification", ""),
        marketing_authorization=first.get("marketing_authorization", MarketingAuthorization.UNKNOWN),
        authorization_number=first.get("authorization_number", ""),
        clinical_investigation=first.get("clinical_investigation", ClinicalInvestigation.UNKNOWN),
        ide_number=first.get("ide_number", ""),
        breakthrough_designation=bool(first.get("breakthrough_designation", False)),
        breakthrough_record=first.get("breakthrough_record"),
        therapeutic_indication=first.get("therapeutic_indication", ""),
        chronic_use=first.get("chronic_use", "NOT_ESTABLISHED"),
    )


def validate_regulatory_state(state: RegulatoryState) -> list[str]:
    """Return a list of internal-contradiction errors (empty = valid)."""
    errors = []
    if state.marketing_authorization == MarketingAuthorization.CLEARANCE_510K:
        if "approval" in state.therapeutic_indication.lower():
            errors.append("510(k) clearance must not be described as 'approval' in "
                          "the therapeutic indication.")
    if state.breakthrough_designation and not state.breakthrough_record:
        errors.append("breakthrough_designation=true requires a breakthrough_record.")
    if state.clinical_investigation == ClinicalInvestigation.IDE_GRANTED and not state.ide_number:
        errors.append("IDE_GRANTED requires an ide_number.")
    if state.marketing_authorization == MarketingAuthorization.PMA_APPROVED and not state.authorization_number:
        errors.append("PMA_APPROVED requires an authorization_number.")
    return errors


def regulatory_to_manifest(state: RegulatoryState) -> dict[str, Any]:
    return {
        "jurisdiction": state.jurisdiction,
        "device": state.device,
        "classification": state.classification,
        "marketing_authorization": state.marketing_authorization,
        "authorization_number": state.authorization_number,
        "clinical_investigation": state.clinical_investigation,
        "ide_number": state.ide_number,
        "breakthrough_designation": state.breakthrough_designation,
        "breakthrough_record": state.breakthrough_record,
        "therapeutic_indication": state.therapeutic_indication,
        "chronic_use": state.chronic_use,
    }


def load_regulatory_yaml(path: str) -> RegulatoryState:
    """Load a regulatory_state.yaml fixture."""
    import yaml
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    records = data.get("regulatory_state", [data])
    state = build_regulatory_state(records)
    errors = validate_regulatory_state(state)
    if errors:
        raise ValueError("regulatory_state.yaml is internally inconsistent: " + "; ".join(errors))
    return state
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_regulatory.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/regulatory.py Test-report-results/tests_v17/test_regulatory.py
git commit -m "feat(engine): typed regulatory ontology with contradiction validation"
```

---

### Task E2: US5215088 `regulatory_state.yaml` fixture

**Files:**
- Create: `evaluations/US5215088/regulatory_state.yaml`
- Test: `Test-report-results/tests_v17/test_regulatory.py`

**Interfaces:**
- Consumes: `load_regulatory_yaml` (Task E1).
- Produces: a committed YAML ontology that validates cleanly and matches the authoritative review.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_regulatory.py
import os
from engine_v17.regulatory import load_regulatory_yaml


def test_us5215088_regulatory_fixture_is_authoritative():
    path = os.path.join(os.path.dirname(__file__), "..", "..",
                        "evaluations", "US5215088", "regulatory_state.yaml")
    st = load_regulatory_yaml(path)
    assert st.marketing_authorization == "510K_CLEARANCE"
    assert st.authorization_number == "K110010"
    assert st.clinical_investigation == "NONE"
    assert st.breakthrough_designation is False
    assert st.breakthrough_record is None
    assert st.chronic_use == "NOT_ESTABLISHED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_regulatory.py -v`
Expected: FAIL — fixture file missing.

- [ ] **Step 3: Create the fixture**

Create `evaluations/US5215088/regulatory_state.yaml`:

```yaml
# v1.9 regulatory ontology — US5215088 / Utah Array / NeuroPort System
# Authoritative facts (from user review):
#   - FDA K110010 = 510(k) CLEARANCE, NOT approval
#   - No IDE established
#   - No breakthrough designation record
#   - Chronic human implantation NOT established as cleared/approved indication
regulatory_state:
  jurisdiction: "United States"
  device: "NeuroPort System / Utah Array (intracortical electrode array)"
  classification: "Class III; 21 CFR 882.8955 (Electrode, Neural, Cortical)"
  marketing_authorization: "510K_CLEARANCE"
  authorization_number: "K110010"
  clinical_investigation: "NONE"
  ide_number: ""
  breakthrough_designation: false
  breakthrough_record: null
  therapeutic_indication: "Short-term intracortical monitoring for research use (510(k) cleared; not FDA-approved for chronic therapeutic use)"
  chronic_use: "NOT_ESTABLISHED"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_regulatory.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add evaluations/US5215088/regulatory_state.yaml Test-report-results/tests_v17/test_regulatory.py
git commit -m "data(eval): add authoritative US5215088 regulatory ontology fixture"
```

---

### Task E3: Renderer consumes the ontology

**Files:**
- Modify: `report-renderer/render_report.py` (`regulatory_table`)
- Test: `report-renderer/tests/test_regulatory_render.py` (new)

**Interfaces:**
- Consumes: `regulatory_state.yaml` via `load_regulatory_yaml` (or a `regulatory_state` dict in the manifest).
- Produces: a Regulatory Status table (authorization type, number, clinical investigation, breakthrough, chronic use) plus a "Precision Guard" note; the renderer aborts if the ontology says clearance and the report text says "approved".

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_regulatory_render.py
import json
import os
import pytest
from render_report import render


@pytest.fixture(scope="module")
def rendered():
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    report_md = open(os.path.join(base, "evaluations", "US5215088", "report.md"), encoding="utf-8").read()
    ledger_md = open(os.path.join(base, "evaluations", "US5215088", "proposition-ledger.json"), encoding="utf-8").read()
    scores = json.load(open(os.path.join(base, "evaluations", "US5215088", "scores-manifest.json"), encoding="utf-8"))
    if "scores_manifest" in scores:
        scores = scores["scores_manifest"]
    return render(report_md, ledger_md, scores)


def test_regulatory_page_shows_clearance_not_approval(rendered):
    assert "510K_CLEARANCE" in rendered
    assert "K110010" in rendered


def test_regulatory_page_shows_no_breakthrough(rendered):
    # The ontology has breakthrough_designation=false; the rendered table
    # must not claim a breakthrough designation.
    assert "Breakthrough Designation" in rendered
    assert "Not designated" in rendered


def test_regulatory_page_shows_chronic_use_not_established(rendered):
    assert "NOT_ESTABLISHED" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_regulatory_render.py -v`
Expected: FAIL — new labels missing.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/render_report.py`, inside `render()`, load the ontology (next to the `reg_data` assignment):

```python
    reg_state = None
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(here), "engine_v17"))
        from regulatory import load_regulatory_yaml as _load_reg_yaml
        _yaml_path = os.path.join(
            os.path.dirname(ledger_path) if ledger_path else here,
            "regulatory_state.yaml")
        if os.path.exists(_yaml_path):
            reg_state = _load_reg_yaml(_yaml_path)
            reg_state_dict = regulatory_to_manifest(reg_state)
        else:
            reg_state_dict = None
    except Exception:
        reg_state_dict = None
```

(Add the matching import `from regulatory import regulatory_to_manifest`.)

Replace `regulatory_table` to render from the ontology when present:

```python
    def regulatory_table(data):
        rows = data.get('rows', [])
        parts = []
        if rows:
            hdr_html = '<th>Jurisdiction</th><th>Body</th><th>Pathway</th><th>Link</th>'
            tbody = ''
            for row in rows:
                tbody += '<tr>' + ''.join('<td>' + md_inline(str(row.get(k, ''))) + '</td>'
                           for k in ['jurisdiction', 'body', 'pathway', 'link']) + '</tr>'
            parts.append('<table class="data"><thead><tr>' + hdr_html + '</tr></thead><tbody>'
                         + tbody + '</tbody></table>')
        if reg_state_dict:
            st = reg_state_dict
            bt = ('Designated' if st.get('breakthrough_designation')
                  else 'Not designated')
            parts.append(
                '<div class="data-frame"><div class="df-title">Regulatory Status (v1.9 ontology)</div>'
                '<table class="data"><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>'
                '<tr><td>Device</td><td>' + md_inline(st.get('device', '')) + '</td></tr>'
                '<tr><td>Classification</td><td>' + md_inline(st.get('classification', '')) + '</td></tr>'
                '<tr><td>Marketing Authorization</td><td>' + html_mod.escape(st.get('marketing_authorization', '')) + '</td></tr>'
                '<tr><td>Authorization Number</td><td>' + html_mod.escape(st.get('authorization_number', '')) + '</td></tr>'
                '<tr><td>Clinical Investigation</td><td>' + html_mod.escape(st.get('clinical_investigation', '')) + '</td></tr>'
                '<tr><td>Breakthrough Designation</td><td>' + html_mod.escape(bt) + '</td></tr>'
                '<tr><td>Chronic Use</td><td>' + html_mod.escape(st.get('chronic_use', '')) + '</td></tr>'
                '<tr><td>Therapeutic Indication</td><td>' + md_inline(st.get('therapeutic_indication', '')) + '</td></tr>'
                '</tbody></table>'
                '<div class="caption">Source: regulatory_state.yaml ontology. '
                '510(k) clearance is not FDA approval; chronic therapeutic use is not established.</div>'
                '</div>')
        if not parts:
            return placeholder_frame('Regulatory Resources')
        return '<div class="data-frame"><div class="df-title">Regulatory Resources</div>' + chr(10).join(parts) + '</div>'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_regulatory_render.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run both full suites + visual QA**

Run:

```bash
python3 -m pytest Test-report-results/tests_v17/ report-renderer/tests/ -q
python3 report-renderer/visual_qa.py 2>&1 | tail -5
```

Expected: all pass; visual QA PASS with the new Regulatory Status table.

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/tests/test_regulatory_render.py
git commit -m "feat(renderer): render regulatory status from typed ontology"
```

---

## Self-Review

**1. Spec coverage:**
- `regulatory_state` YAML ontology → Task E2 (committed fixture, loads via PyYAML 6.0.3).
- jurisdiction / device / classification / marketing_authorization / clinical_investigation / breakthrough_designation / therapeutic_indication / chronic_use → Task E1 (all fields on `RegulatoryState`).
- FDA K110010 = 510(k) clearance (not approval), no IDE, no breakthrough → Task E2 (authoritative fixture values) + Task E1 (validation rules prevent "approval"/"breakthrough"/"IDE" overclaims) + Task E3 (renderer renders clearance, Not designated, NOT_ESTABLISHED).

**2. Placeholder scan:** No TBD/TODO; every step has concrete code and expected output.

**3. Type consistency:** `MarketingAuthorization`/`ClinicalInvestigation` are string-constant classes (matching the renderer contract's style); `validate_regulatory_state` returns `list[str]`; `regulatory_to_manifest` output keys match the renderer's lookups; YAML `regulatory_state` root maps to `build_regulatory_state(records)` with a single record.