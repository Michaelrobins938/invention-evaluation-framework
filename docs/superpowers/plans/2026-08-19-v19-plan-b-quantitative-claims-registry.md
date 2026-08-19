# Plan B — v1.9 Quantitative Claims Registry: Typed Numbers with Provenance

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote every quantitative statement in the report from free-text (e.g. `*[LLM_INFERENCE]*` inline tags in Market Analysis) to a first-class, typed `QuantitativeClaim` object carrying source type, date, population, comparison group, scope, epistemic state, and confidence. The renderer consumes these objects to label every number with its provenance instead of relying on hand-written inline tags.

**Architecture:** A new engine module `engine_v17/claims.py` defines `SourceType` and `QuantitativeClaim`. The scores manifest gains a top-level `quantitative_claims` array (sibling of `scores`). The renderer's data-frame generators (`market_opp_table`, `regulatory_table`, `patentability_table`) read the array and render a provenance column per row. The US5215088 fixture is migrated: the $3.25B / 14.5% CAGR / market-share figures become `QuantitativeClaim` records with `source_type=LLM_INFERENCE`, `epistemic_state=PARTIALLY_ESTABLISHED` (directional) or `NOT_ESTABLISHED` (specific numbers), and the inline `*[LLM_INFERENCE]*` tags in report.md are removed (the renderer now owns that labeling).

**Tech Stack:** Python 3.10+ (repo runs 3.14), pytest, dataclasses + `Enum`, JSON manifests.

## Global Constraints

- Canonical `SourceType` values: `LLM_INFERENCE`, `INDUSTRY_BENCHMARK`, `STRUCTURED_DATABASE`, `COMPANY_REPORTED`, `REGULATORY_RECORD`, `PEER_REVIEWED`.
- A `QuantitativeClaim` MUST carry: `claim_id`, `proposition_id`, `metric`, `value` (string, preserves "~$3.25B" formatting), `unit`, `source_type`, `source`, `date`, `population`, `comparison_group`, `scope`, `epistemic_state`, `confidence`, `note`.
- `epistemic_state` uses the canonical v1.9 values from Plan A (`ESTABLISHED`, `PARTIALLY_ESTABLISHED`, `NOT_ESTABLISHED`, `CONTRADICTED`). Directional claims (e.g. "market growing") may be `PARTIALLY_ESTABLISHED`; specific numbers without a structured-database source are `NOT_ESTABLISHED` unless independently verified.
- US5215088 fixture (authoritative, from user review): $3.25B TAM → `LLM_INFERENCE` + `NOT_ESTABLISHED`; 14.5% CAGR → `LLM_INFERENCE` + `NOT_ESTABLISHED`; research share 35–40% → `LLM_INFERENCE` + `NOT_ESTABLISHED`; human BCI share ~90% → `LLM_INFERENCE` + `NOT_ESTABLISHED`; Blackrock revenue $40–60M → `COMPANY_REPORTED` + `PARTIALLY_ESTABLISHED` (publicly reported range, not audited). All five map to proposition P-07-001 (scope `MARKET`).
- The renderer MUST NOT invent a source type for a claim that lacks one; missing `source_type` fails validation.
- No report-specific hand-fixes. All changes are engine/renderer-level; the fixture migration is data, not code.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`).

## File Structure

- `engine_v17/claims.py` — new: `SourceType`, `QuantitativeClaim`, `parse_claims()`, `validate_claims()`, `claims_to_manifest()`.
- `evaluations/US5215088/scores-manifest.json` — add `quantitative_claims` array (migrated fixture).
- `report-renderer/render_report.py` — `market_opp_table` (and `regulatory_table`/`patentability_table` where applicable) render provenance columns from the claims array.
- `Test-report-results/tests_v17/test_claims.py` — new engine tests.
- `report-renderer/tests/test_claims_render.py` — new renderer tests.

---

### Task B1: `SourceType` + `QuantitativeClaim` in `engine_v17/claims.py`

**Files:**
- Create: `engine_v17/claims.py`
- Test: `Test-report-results/tests_v17/test_claims.py` (new)

**Interfaces:**
- Consumes: `EpistemicState`, `RecoveryState`, `Scope` from `engine_v17/models.py` (Plan A Task A1).
- Produces: `SourceType` enum; `QuantitativeClaim` dataclass with `to_dict()` / `from_dict()`; `parse_claims(raw: list[dict]) -> list[QuantitativeClaim]` that raises `ValueError` on missing `source_type`.

- [ ] **Step 1: Write the failing test**

```python
# Test-report-results/tests_v17/test_claims.py
import pytest
from engine_v17.claims import SourceType, QuantitativeClaim, parse_claims
from engine_v17.models import EpistemicState, Scope


def test_source_type_has_all_six_values():
    assert {s.value for s in SourceType} == {
        "LLM_INFERENCE", "INDUSTRY_BENCHMARK", "STRUCTURED_DATABASE",
        "COMPANY_REPORTED", "REGULATORY_RECORD", "PEER_REVIEWED",
    }


def test_quantitative_claim_round_trip():
    c = QuantitativeClaim(
        claim_id="Q-07-001",
        proposition_id="P-07-001",
        metric="BCI total addressable market",
        value="~$3.25B",
        unit="USD",
        source_type=SourceType.LLM_INFERENCE,
        source="LLM synthesis of industry reports",
        date="2026-08-19",
        population="global BCI devices + intracortical electrodes + neuroprosthetics + visual prostheses",
        comparison_group="none",
        scope=Scope.MARKET,
        epistemic_state=EpistemicState.NOT_ESTABLISHED,
        confidence="LOW",
        note="Directional only; no structured market database consulted",
    )
    d = c.to_dict()
    assert d["source_type"] == "LLM_INFERENCE"
    assert d["epistemic_state"] == "NOT_ESTABLISHED"
    assert d["scope"] == "MARKET"
    c2 = QuantitativeClaim.from_dict(d)
    assert c2 == c


def test_parse_claims_requires_source_type():
    with pytest.raises(ValueError):
        parse_claims([{"claim_id": "Q-07-002", "metric": "CAGR", "value": "14.5%"}])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_claims.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine_v17.claims'`

- [ ] **Step 3: Write minimal implementation**

Create `engine_v17/claims.py`:

```python
"""v1.9 quantitative claims registry.

Every number in a report is a first-class object with provenance:
source type, date, population, comparison group, scope, epistemic
state, and confidence. The renderer labels numbers from this registry
instead of relying on hand-written inline tags in report.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import EpistemicState, Scope


class SourceType:
    """Provenance class of a quantitative claim."""
    LLM_INFERENCE = "LLM_INFERENCE"
    INDUSTRY_BENCHMARK = "INDUSTRY_BENCHMARK"
    STRUCTURED_DATABASE = "STRUCTURED_DATABASE"
    COMPANY_REPORTED = "COMPANY_REPORTED"
    REGULATORY_RECORD = "REGULATORY_RECORD"
    PEER_REVIEWED = "PEER_REVIEWED"

    _ALL = {
        LLM_INFERENCE, INDUSTRY_BENCHMARK, STRUCTURED_DATABASE,
        COMPANY_REPORTED, REGULATORY_RECORD, PEER_REVIEWED,
    }


@dataclass
class QuantitativeClaim:
    """One typed quantitative statement with full provenance."""
    claim_id: str
    proposition_id: str
    metric: str
    value: str                       # preserves original formatting ("~$3.25B")
    unit: str = ""
    source_type: str = SourceType.LLM_INFERENCE
    source: str = ""
    date: str = ""
    population: str = ""
    comparison_group: str = ""
    scope: str = Scope.TARGET_PATENT
    epistemic_state: str = EpistemicState.NOT_ESTABLISHED
    confidence: str = "LOW"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "proposition_id": self.proposition_id,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "source_type": self.source_type,
            "source": self.source,
            "date": self.date,
            "population": self.population,
            "comparison_group": self.comparison_group,
            "scope": self.scope,
            "epistemic_state": self.epistemic_state,
            "confidence": self.confidence,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuantitativeClaim":
        return cls(
            claim_id=data["claim_id"],
            proposition_id=data.get("proposition_id", ""),
            metric=data.get("metric", ""),
            value=data.get("value", ""),
            unit=data.get("unit", ""),
            source_type=data.get("source_type", SourceType.LLM_INFERENCE),
            source=data.get("source", ""),
            date=data.get("date", ""),
            population=data.get("population", ""),
            comparison_group=data.get("comparison_group", ""),
            scope=data.get("scope", Scope.TARGET_PATENT),
            epistemic_state=data.get("epistemic_state", EpistemicState.NOT_ESTABLISHED),
            confidence=data.get("confidence", "LOW"),
            note=data.get("note", ""),
        )


def parse_claims(raw: list[dict[str, Any]]) -> list[QuantitativeClaim]:
    """Parse a manifest ``quantitative_claims`` array.

    Raises ValueError if any claim lacks a source_type — the renderer must
    never invent provenance for a number.
    """
    claims = []
    for item in raw:
        st = item.get("source_type")
        if not st or st not in SourceType._ALL:
            raise ValueError(
                f"claim {item.get('claim_id', '?')} missing or invalid source_type")
        claims.append(QuantitativeClaim.from_dict(item))
    return claims
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_claims.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/claims.py Test-report-results/tests_v17/test_claims.py
git commit -m "feat(engine): add quantitative claims registry with source-type provenance"
```

---

### Task B2: Migrate the US5215088 manifest with authoritative claims

**Files:**
- Modify: `evaluations/US5215088/scores-manifest.json` (data migration)
- Test: `Test-report-results/tests_v17/test_claims.py`

**Interfaces:**
- Consumes: `parse_claims` (Task B1).
- Produces: `quantitative_claims` array in the manifest; `parse_claims` round-trips it without error.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_claims.py
import json
import os


def test_us5215088_manifest_claims_parse_and_are_authoritative():
    path = os.path.join(os.path.dirname(__file__), "..", "..",
                        "evaluations", "US5215088", "scores-manifest.json")
    manifest = json.load(open(path, encoding="utf-8"))["scores_manifest"]
    claims = parse_claims(manifest.get("quantitative_claims", []))
    by_id = {c.claim_id: c for c in claims}
    assert by_id["Q-07-001"].value == "~$3.25B"
    assert by_id["Q-07-001"].source_type == "LLM_INFERENCE"
    assert by_id["Q-07-001"].epistemic_state == "NOT_ESTABLISHED"
    assert by_id["Q-07-001"].proposition_id == "P-07-001"
    assert by_id["Q-07-005"].source_type == "COMPANY_REPORTED"
    assert by_id["Q-07-005"].epistemic_state == "PARTIALLY_ESTABLISHED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_claims.py -v`
Expected: FAIL — `quantitative_claims` missing from the manifest (empty list).

- [ ] **Step 3: Add the claims array to the manifest**

Run:

```bash
python3 - <<'EOF'
import json
path = "evaluations/US5215088/scores-manifest.json"
manifest = json.load(open(path, encoding="utf-8"))["scores_manifest"]
manifest["quantitative_claims"] = [
    {
        "claim_id": "Q-07-001",
        "proposition_id": "P-07-001",
        "metric": "BCI total addressable market (devices + intracortical electrodes + neuroprosthetics + visual prostheses)",
        "value": "~$3.25B",
        "unit": "USD",
        "source_type": "LLM_INFERENCE",
        "source": "LLM synthesis of industry reports; no structured market database consulted",
        "date": "2026-08-19",
        "population": "global",
        "comparison_group": "none",
        "scope": "MARKET",
        "epistemic_state": "NOT_ESTABLISHED",
        "confidence": "LOW",
        "note": "Directional only. Specific number is NOT established.",
    },
    {
        "claim_id": "Q-07-002",
        "proposition_id": "P-07-001",
        "metric": "BCI market CAGR",
        "value": "14.5%",
        "unit": "percent",
        "source_type": "LLM_INFERENCE",
        "source": "LLM synthesis of industry reports",
        "date": "2026-08-19",
        "population": "global",
        "comparison_group": "none",
        "scope": "MARKET",
        "epistemic_state": "NOT_ESTABLISHED",
        "confidence": "LOW",
        "note": "Specific number is NOT established.",
    },
    {
        "claim_id": "Q-07-003",
        "proposition_id": "P-07-001",
        "metric": "Utah Array research market share",
        "value": "35-40%",
        "unit": "percent",
        "source_type": "LLM_INFERENCE",
        "source": "LLM synthesis of industry reports",
        "date": "2026-08-19",
        "population": "research BCI market",
        "comparison_group": "other intracortical electrode vendors",
        "scope": "MARKET",
        "epistemic_state": "NOT_ESTABLISHED",
        "confidence": "LOW",
        "note": "Range is directional, not audited.",
    },
    {
        "claim_id": "Q-07-004",
        "proposition_id": "P-07-001",
        "metric": "Utah Array human BCI market share",
        "value": "~90%+",
        "unit": "percent",
        "source_type": "LLM_INFERENCE",
        "source": "LLM synthesis of industry reports",
        "date": "2026-08-19",
        "population": "human BCI implant market",
        "comparison_group": "all human BCI implant vendors",
        "scope": "MARKET",
        "epistemic_state": "NOT_ESTABLISHED",
        "confidence": "LOW",
        "note": "Directional dominance claim; exact share NOT established.",
    },
    {
        "claim_id": "Q-07-005",
        "proposition_id": "P-07-001",
        "metric": "Blackrock Neurotech estimated annual revenue",
        "value": "$40-60M",
        "unit": "USD",
        "source_type": "COMPANY_REPORTED",
        "source": "Publicly reported company figures (not audited)",
        "date": "2026-08-19",
        "population": "Blackrock Neurotech",
        "comparison_group": "none",
        "scope": "COMMERCIAL_PRODUCT",
        "epistemic_state": "PARTIALLY_ESTABLISHED",
        "confidence": "MODERATE",
        "note": "Company-reported range; treat as directional.",
    },
]
json.dump({"scores_manifest": manifest}, open(path, "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print("quantitative_claims added:", len(manifest["quantitative_claims"]))
EOF
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_claims.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add evaluations/US5215088/scores-manifest.json Test-report-results/tests_v17/test_claims.py
git commit -m "feat(data): add authoritative quantitative claims to US5215088 manifest"
```

---

### Task B3: Renderer labels numbers from the claims registry

**Files:**
- Modify: `report-renderer/render_report.py` (`market_opp_table`, `regulatory_table`, `patentability_table`)
- Test: `report-renderer/tests/test_claims_render.py` (new)

**Interfaces:**
- Consumes: `quantitative_claims` array from the scores manifest (Task B2).
- Produces: provenance labels (`source_type` + `epistemic_state`) rendered per row in the Opportunity Assessment table; a `Claims Provenance` data-frame appended to the Market Analysis page.

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_claims_render.py
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


def test_market_page_renders_claims_provenance_frame(rendered):
    assert "Claims Provenance" in rendered


def test_market_page_labels_llm_inference(rendered):
    assert "LLM_INFERENCE" in rendered


def test_market_page_labels_not_established(rendered):
    assert "NOT_ESTABLISHED" in rendered


def test_market_page_labels_company_reported(rendered):
    assert "COMPANY_REPORTED" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_claims_render.py -v`
Expected: FAIL — `Claims Provenance` not in output.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/render_report.py`, inside `render()`, after the `market_op`/`comp`/`reg_data` assignments (line ~614), add:

```python
    claims = scores.get('quantitative_claims', [])

    def claims_provenance_frame(claims_data):
        if not claims_data:
            return placeholder_frame('Claims Provenance')
        rows = ''.join(
            '<tr><td>' + html_mod.escape(c.get('claim_id', '')) + '</td>'
            '<td>' + md_inline(c.get('metric', '')) + '</td>'
            '<td>' + md_inline(c.get('value', '')) + '</td>'
            '<td><span class="src-tag">' + html_mod.escape(c.get('source_type', 'UNKNOWN')) + '</span></td>'
            '<td>' + html_mod.escape(c.get('epistemic_state', 'NOT_ESTABLISHED')) + '</td>'
            '<td>' + html_mod.escape(c.get('confidence', '')) + '</td>'
            '<td>' + md_inline(c.get('note', '')) + '</td></tr>'
            for c in claims_data)
        return ('<div class="data-frame"><div class="df-title">Claims Provenance</div>'
                '<table class="data"><thead><tr>'
                '<th>Claim</th><th>Metric</th><th>Value</th><th>Source Type</th>'
                '<th>Epistemic State</th><th>Confidence</th><th>Note</th>'
                '</tr></thead><tbody>' + rows + '</tbody></table></div>')
```

Then append the frame to the Opportunity Assessment page (after the `market_opp_table(market_op)` page, around line 790):

```python
    body_html.append('<div class="page"><h2 class="section-title">Claims Provenance</h2>'
                     + claims_provenance_frame(claims) + '</div>')
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_claims_render.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the full renderer suite**

Run: `python3 -m pytest report-renderer/tests/ -q`
Expected: all existing tests still pass.

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/tests/test_claims_render.py
git commit -m "feat(renderer): render quantitative claims provenance from manifest"
```

---

### Task B4: Remove inline `*[LLM_INFERENCE]*` tags from report.md

**Files:**
- Modify: `evaluations/US5215088/report.md` (data cleanup)
- Test: `report-renderer/tests/test_claims_render.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: report.md without inline provenance tags; the renderer owns provenance labeling now.

- [ ] **Step 1: Write the failing test**

```python
# append to report-renderer/tests/test_claims_render.py
def test_report_md_has_no_inline_provenance_tags():
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    report_md = open(os.path.join(base, "evaluations", "US5215088", "report.md"), encoding="utf-8").read()
    assert "[LLM_INFERENCE]" not in report_md
    assert "[PRECISION REQUIRED]" not in report_md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_claims_render.py -v`
Expected: FAIL — inline tags still present.

- [ ] **Step 3: Remove the inline tags**

Edit `evaluations/US5215088/report.md`:
- Remove ` *[LLM_INFERENCE]*` from the Market Size, Growth Rate, and Utah Array Market Position lines (lines 198, 200, 202).
- Remove ` *[PRECISION REQUIRED]*` from the FDA Regulatory Status line (line 229).
- Keep the EPISTEMIC NOTE paragraph at the top of Section 5 (it is a human-readable summary; the machine-checkable provenance now lives in the manifest).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_claims_render.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Re-render the v18 HTML/PDF and run visual QA**

Run:

```bash
python3 -m pytest report-renderer/tests/ -q
python3 report-renderer/visual_qa.py 2>&1 | tail -5
```

Expected: all tests pass; visual QA PASS.

- [ ] **Step 6: Commit**

```bash
git add evaluations/US5215088/report.md report-renderer/tests/test_claims_render.py
git commit -m "docs(data): remove inline provenance tags; renderer owns claim labeling"
```

---

## Self-Review

**1. Spec coverage:**
- Quantitative claims as first-class objects → Tasks B1, B3.
- Source types (LLM_INFERENCE / INDUSTRY_BENCHMARK / STRUCTURED_DATABASE / COMPANY_REPORTED / REGULATORY_RECORD / PEER_REVIEWED) → Task B1.
- date / population / comparison_group / scope / epistemic_state / confidence → Task B1 (dataclass fields).
- Market figures relabeled Established/Estimated/Unknown → Task B2 (authoritative fixture: NOT_ESTABLISHED for LLM-inferred numbers, PARTIALLY_ESTABLISHED for company-reported).
- Renderer consumes labels instead of hand-written tags → Tasks B3, B4.

**2. Placeholder scan:** No TBD/TODO; every step has concrete code and expected output.

**3. Type consistency:** `QuantitativeClaim.source_type` is a string constant (matching the renderer contract's string-constant pattern from Plan A); `parse_claims` validates against `SourceType._ALL`; manifest keys match `from_dict` expectations; `epistemic_state` values are the canonical v1.9 strings.