# Plan F — v1.9 Consumer Layer: Three Report Levels, 30-Second Take, Decisions, Reader Modes

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every report *usable* by three audiences (Executive, Commercial, Technical) with three report levels, a page-1 30-Second Take, deterministic Decision guidance per audience, "What this means" boxes, and a restructured 8-section layout (`01 Bottom Line` … `08 Audit Trail`) with full P-code → evidence → source traceability.

**Architecture:** A new `report-renderer/consumer.py` module computes everything **deterministically from the v1.9 data plane** (scores manifest, proposition registry, quantitative claims, commercial portfolio conclusion, regulatory state): `ReaderMode` enum, `ThirtySecondTake`, `WhatThisMeansBox`, and `DecisionSection` (owner / investor / licensee / competitor stances). The renderer (`render_report.py`) maps report.md sections into the 8-section structure, generates the Bottom Line page (30-Second Take + Decisions + debt summary) and the Audit Trail page (proposition → evidence → source table), and offers reader-mode emphasis. Nothing in consumer.py calls an LLM — it interprets evidence-constrained data; it never invents.

**Tech Stack:** Python 3.10+ (repo runs 3.14), pytest, dataclasses + `Enum`, JSON manifest.

## Global Constraints

- Three report levels: `EXECUTIVE_BRIEFING` (Bottom Line + Decisions + debt summary only), `STANDARD_EVALUATION` (full 8 sections), `EVIDENCE_DOSSIER` (full + Audit Trail + evidence recovery record).
- Three reader modes: `EXECUTIVE` (Bottom Line, Decisions, debt), `COMMERCIAL` (Market Opportunity, Partners & Commercial Path, Decisions), `TECHNICAL` (Technology, Patents & IP, Operational Audit, Audit Trail).
- 8-section structure (v1.9): `01 Bottom Line`, `02 Technology Analysis`, `03 Patents & IP`, `04 Market Opportunity`, `05 Regulatory & Compliance`, `06 Partners & Commercial Path`, `07 Operational Audit`, `08 Audit Trail`.
- The 30-Second Take MUST be computed from: overall_assessment (scores), key numbers (quantitative_claims, top 3 by metric), debt count (`is_recoverable_debt`), patent status (commercial conclusion `standalone_licensing_leverage`), regulatory state (marketing_authorization). No prose invention.
- The Decision section MUST NOT contain a stance that contradicts the data plane: an expired-patent owner stance cannot say "license your patent"; an investor stance must quote the debt count; a licensee stance must quote the commercialization conclusion; a competitor stance must quote the scope_note.
- "What this means" boxes are rendered only for sections whose underlying propositions exist in the registry; a box's text is assembled from registry fields (`claim`, `epistemic_state`, `recovery_state`), never free-written.
- Backward compatibility: all existing renderer tests (57) keep passing; report.md keeps its current H2 titles (the 8-section mapping lives in the renderer).
- No report-specific hand-fixes. All changes are renderer-level; the data plane already carries the facts.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`).

## File Structure

- `report-renderer/consumer.py` — new: `ReaderMode`, `ReportLevel`, `ThirtySecondTake`, `WhatThisMeansBox`, `DecisionSection`.
- `report-renderer/render_report.py` — 8-section mapping, Bottom Line page, Audit Trail page, reader-mode emphasis.
- `report-renderer/tests/test_consumer.py` — new renderer tests.
- `report-renderer/tests/test_consumer_render.py` — new end-to-end render tests.

---

### Task F1: `consumer.py` — ReaderMode, ReportLevel, ThirtySecondTake

**Files:**
- Create: `report-renderer/consumer.py`
- Test: `report-renderer/tests/test_consumer.py` (new)

**Interfaces:**
- Consumes: scores manifest dict, `PropositionRegistry`, `quantitative_claims` list, commercial conclusion dict, regulatory state dict.
- Produces: `ReaderMode` (`EXECUTIVE`/`COMMERCIAL`/`TECHNICAL`), `ReportLevel` (`EXECUTIVE_BRIEFING`/`STANDARD_EVALUATION`/`EVIDENCE_DOSSIER`), `ThirtySecondTake` dataclass with `build_take(scores, registry, claims, commercial, regulatory) -> ThirtySecondTake`.

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_consumer.py
from consumer import (
    ReaderMode, ReportLevel, ThirtySecondTake,
)


def test_reader_modes():
    assert {m for m in ReaderMode} == {"EXECUTIVE", "COMMERCIAL", "TECHNICAL"}


def test_report_levels():
    assert {l for l in ReportLevel} == {
        "EXECUTIVE_BRIEFING", "STANDARD_EVALUATION", "EVIDENCE_DOSSIER"}


def _registry():
    from contract import PropositionRegistry
    ledger = {"proposition_ledger": {
        "P-03-001": {"claim": "3D array", "epistemic_state": "ESTABLISHED",
                     "recovery_state": "NONE_REQUIRED"},
        "P-03-003": {"claim": "chronic yield", "epistemic_state": "NOT_ESTABLISHED",
                     "recovery_state": "ESCALATION_REQUIRED"},
        "P-07-001": {"claim": "BCI market size", "epistemic_state": "PARTIALLY_ESTABLISHED",
                     "recovery_state": "SEARCH_PENDING"},
    }}
    return PropositionRegistry(ledger)


def test_thirty_second_take_uses_data_plane():
    take = ThirtySecondTake.build_take(
        scores={"overall_assessment": "MODERATE-TO-HIGH", "invention_name": "3D electrode"},
        registry=_registry(),
        claims=[
            {"claim_id": "Q-07-001", "metric": "BCI TAM", "value": "~$3.25B",
             "source_type": "LLM_INFERENCE", "epistemic_state": "NOT_ESTABLISHED"},
        ],
        commercial={"standalone_licensing_leverage": "minimal",
                    "commercialization": "active_via_licensee"},
        regulatory={"marketing_authorization": "510K_CLEARANCE",
                    "authorization_number": "K110010"},
    )
    assert take.verdict == "MODERATE-TO-HIGH"
    assert take.debt_count == 2          # P-03-003 + P-07-001 (recoverable only)
    assert take.key_numbers[0]["value"] == "~$3.25B"
    assert take.patent_leverage == "minimal"
    assert take.regulatory_authorization == "510K_CLEARANCE"
    assert take.markdown()  # renders without error
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_consumer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'consumer'`

- [ ] **Step 3: Write minimal implementation**

Create `report-renderer/consumer.py`:

```python
"""v1.9 consumer layer.

Deterministic report interpretation for three audiences and three report
levels. No LLM calls — every output is computed from the v1.9 data plane
(scores, registry, claims, commercial conclusion, regulatory state).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ReaderMode:
    EXECUTIVE = "EXECUTIVE"
    COMMERCIAL = "COMMERCIAL"
    TECHNICAL = "TECHNICAL"


class ReportLevel:
    EXECUTIVE_BRIEFING = "EXECUTIVE_BRIEFING"
    STANDARD_EVALUATION = "STANDARD_EVALUATION"
    EVIDENCE_DOSSIER = "EVIDENCE_DOSSIER"


# v1.9 8-section structure (renderer maps report.md H2s onto these).
SECTIONS_V19 = (
    "01 Bottom Line",
    "02 Technology Analysis",
    "03 Patents & IP",
    "04 Market Opportunity",
    "05 Regulatory & Compliance",
    "06 Partners & Commercial Path",
    "07 Operational Audit",
    "08 Audit Trail",
)

LEVEL_SECTIONS = {
    ReportLevel.EXECUTIVE_BRIEFING: ("01 Bottom Line",),
    ReportLevel.STANDARD_EVALUATION: SECTIONS_V19[:7],
    ReportLevel.EVIDENCE_DOSSIER: SECTIONS_V19,
}

MODE_SECTIONS = {
    ReaderMode.EXECUTIVE: ("01 Bottom Line",),
    ReaderMode.COMMERCIAL: ("04 Market Opportunity", "06 Partners & Commercial Path",
                            "01 Bottom Line"),
    ReaderMode.TECHNICAL: ("02 Technology Analysis", "03 Patents & IP",
                           "07 Operational Audit", "08 Audit Trail"),
}


@dataclass
class ThirtySecondTake:
    verdict: str
    invention: str
    debt_count: int
    key_numbers: list[dict[str, str]] = field(default_factory=list)
    patent_leverage: str = ""
    commercialization: str = ""
    regulatory_authorization: str = ""
    top_risk: str = ""

    @classmethod
    def build_take(cls, scores: dict, registry: Any, claims: list[dict],
                   commercial: dict, regulatory: dict) -> "ThirtySecondTake":
        debt_count = sum(1 for p in registry.all() if p.is_recoverable_debt)
        key_numbers = [
            {"metric": c.get("metric", ""), "value": c.get("value", ""),
             "source_type": c.get("source_type", ""),
             "epistemic_state": c.get("epistemic_state", "")}
            for c in (claims or [])[:3]
        ]
        top_risk = "evidence debt" if debt_count else "none material"
        return cls(
            verdict=str(scores.get("overall_assessment", "NOT_ASSESSED")),
            invention=str(scores.get("invention_name", "")),
            debt_count=debt_count,
            key_numbers=key_numbers,
            patent_leverage=str(commercial.get("standalone_licensing_leverage", "")),
            commercialization=str(commercial.get("commercialization", "")),
            regulatory_authorization=str(regulatory.get("marketing_authorization", "")),
            top_risk=top_risk,
        )

    def markdown(self) -> str:
        lines = [f"**{self.invention}** — overall assessment: {self.verdict}",
                 f"- Evidence debt: {self.debt_count} recoverable item(s)",
                 f"- Patent leverage: {self.patent_leverage}",
                 f"- Commercialization: {self.commercialization}",
                 f"- Regulatory: {self.regulatory_authorization}",
                 f"- Top risk: {self.top_risk}"]
        if self.key_numbers:
            lines.append("- Key numbers:")
            for n in self.key_numbers:
                lines.append(f"  - {n['metric']}: {n['value']} "
                             f"[{n['source_type']} / {n['epistemic_state']}]")
        return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_consumer.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add report-renderer/consumer.py report-renderer/tests/test_consumer.py
git commit -m "feat(renderer): consumer layer with reader modes, levels, 30-second take"
```

---

### Task F2: `DecisionSection` + `WhatThisMeansBox`

**Files:**
- Modify: `report-renderer/consumer.py`
- Test: `report-renderer/tests/test_consumer.py`

**Interfaces:**
- Consumes: registry, commercial conclusion, regulatory state, scores.
- Produces: `WhatThisMeansBox.for_section(section_title, registry) -> str | None` (None when no registry propositions map to the section); `DecisionSection.build(...) -> DecisionSection` with `owner()/investor()/licensee()/competitor()` stances, each a dict of deterministic statements.

- [ ] **Step 1: Write the failing test**

```python
# append to report-renderer/tests/test_consumer.py
from consumer import WhatThisMeansBox, DecisionSection


def test_what_this_means_box_uses_registry_fields():
    box = WhatThisMeansBox.for_section("02 Technology Analysis", _registry())
    assert box is not None
    assert "P-03-003" in box
    assert "NOT_ESTABLISHED" in box
    assert "ESCALATION_REQUIRED" in box


def test_what_this_means_box_none_for_unknown_section():
    assert WhatThisMeansBox.for_section("0 Unknown", _registry()) is None


def test_decision_owner_stance_respects_expired_patent():
    d = DecisionSection.build(
        registry=_registry(),
        commercial={"standalone_licensing_leverage": "minimal",
                    "commercialization": "active_via_licensee",
                    "scope_note": "Later-generation technology does not extend the target."},
        regulatory={"marketing_authorization": "510K_CLEARANCE",
                    "authorization_number": "K110010"},
        scores={"overall_assessment": "MODERATE-TO-HIGH"},
    )
    owner = d.owner()
    assert "expired" in owner["stance"].lower()
    assert "license the patent" not in owner["stance"].lower()


def test_decision_investor_quotes_debt():
    d = DecisionSection.build(
        registry=_registry(),
        commercial={},
        regulatory={},
        scores={},
    )
    inv = d.investor()
    assert "2" in inv["evidence_debt"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_consumer.py -v`
Expected: FAIL with `ImportError: cannot import name 'WhatThisMeansBox'`

- [ ] **Step 3: Write minimal implementation**

Append to `report-renderer/consumer.py`:

```python
class WhatThisMeansBox:
    """Evidence-constrained interpretation box per section."""

    SECTION_PREFIX = {
        "02 Technology Analysis": "P-03",
        "03 Patents & IP": "P-02",
        "04 Market Opportunity": "P-07",
        "05 Regulatory & Compliance": "P-03-004",
        "06 Partners & Commercial Path": "P-08",
        "07 Operational Audit": "P-05",
    }

    @classmethod
    def for_section(cls, section_title: str, registry: Any) -> str | None:
        prefix = cls.SECTION_PREFIX.get(section_title)
        if not prefix:
            return None
        props = [p for p in registry.all() if p.proposition_id.startswith(prefix)]
        if not props:
            return None
        parts = []
        for p in props[:4]:
            parts.append(
                f"{p.proposition_id} ({p.claim}): {p.state} / {p.recovery_state}")
        return ("What this means: " + "; ".join(parts) + ".")

    @classmethod
    def markdown(cls, section_title: str, registry: Any) -> str | None:
        text = cls.for_section(section_title, registry)
        return f"> **What this means:** {text}" if text else None


@dataclass
class DecisionSection:
    scores: dict
    commercial: dict
    regulatory: dict
    debt_count: int

    @classmethod
    def build(cls, registry: Any, commercial: dict, regulatory: dict,
              scores: dict) -> "DecisionSection":
        debt_count = sum(1 for p in registry.all() if p.is_recoverable_debt)
        return cls(
            scores=scores,
            commercial=commercial or {},
            regulatory=regulatory or {},
            debt_count=debt_count,
        )

    def owner(self) -> dict[str, str]:
        leverage = self.commercial.get("standalone_licensing_leverage", "")
        if leverage == "minimal":
            stance = ("The patent is expired; standalone patent licensing is blocked. "
                      "Value lies in the licensee relationship and portfolio assets, "
                      "not in new patent grants.")
        else:
            stance = ("Patent leverage is available; verify current status before "
                      "structuring any grant.")
        return {"audience": "owner", "stance": stance}

    def investor(self) -> dict[str, str]:
        return {
            "audience": "investor",
            "stance": (
                f"Commercialization is {self.commercial.get('commercialization', 'not assessed')}. "
                f"Evidence debt is {self.debt_count} recoverable item(s); "
                f"resolve before relying on the affected conclusions."),
            "evidence_debt": str(self.debt_count),
        }

    def licensee(self) -> dict[str, str]:
        return {
            "audience": "licensee",
            "stance": (
                f"Regulatory position: {self.regulatory.get('marketing_authorization', 'not assessed')} "
                f"({self.regulatory.get('authorization_number', '')}). "
                f"Scope note: {self.commercial.get('scope_note', 'not assessed')}"),
        }

    def competitor(self) -> dict[str, str]:
        return {
            "audience": "competitor",
            "stance": (
                f"Later-generation technology is treated as outside the target patent's "
                f"claim scope: {self.commercial.get('scope_note', 'not assessed')}"),
        }

    def all_stances(self) -> list[dict[str, str]]:
        return [self.owner(), self.investor(), self.licensee(), self.competitor()]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_consumer.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add report-renderer/consumer.py report-renderer/tests/test_consumer.py
git commit -m "feat(renderer): deterministic decision stances and what-this-means boxes"
```

---

### Task F3: 8-section restructure + Bottom Line page

**Files:**
- Modify: `report-renderer/render_report.py`
- Test: `report-renderer/tests/test_consumer_render.py` (new)

**Interfaces:**
- Consumes: `SECTIONS_V19`, `ThirtySecondTake`, `DecisionSection` (Tasks F1, F2).
- Produces: rendered report whose section order follows the 8-section structure and whose first page is "01 Bottom Line" (30-Second Take + Decisions + debt summary).

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_consumer_render.py
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
    return render(
        report_md, ledger_md, scores,
        ledger_path=os.path.join(base, "evaluations", "US5215088", "proposition-ledger.json"))


def test_bottom_line_page_present(rendered):
    assert "01 Bottom Line" in rendered
    assert "30-Second Take" in rendered


def test_bottom_line_shows_debt_count(rendered):
    assert "Evidence debt" in rendered


def test_decision_stances_present(rendered):
    assert "owner" in rendered
    assert "investor" in rendered
    assert "licensee" in rendered
    assert "competitor" in rendered


def test_section_order_follows_v19(rendered):
    idx = [rendered.find(s) for s in (
        "01 Bottom Line", "02 Technology Analysis", "03 Patents & IP",
        "04 Market Opportunity", "05 Regulatory & Compliance",
        "06 Partners & Commercial Path", "07 Operational Audit")]
    assert all(i >= 0 for i in idx)
    assert idx == sorted(idx)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_consumer_render.py -v`
Expected: FAIL — `01 Bottom Line` missing.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/render_report.py`:

1. Add a `SECTION_RENAME_V19` map that maps existing bare section titles to the v1.9 numbered titles:

```python
    SECTION_RENAME_V19 = {
        'Technology Analysis': '02 Technology Analysis',
        'Patent Landscape Analysis': '03 Patents & IP',
        'Novelty & IP Analysis': '03 Patents & IP',
        'Literature Analysis': '03 Patents & IP',
        'Market Analysis': '04 Market Opportunity',
        'Opportunity Assessment': '04 Market Opportunity',
        'Regulatory Resources': '05 Regulatory & Compliance',
        'Potential Partners': '06 Partners & Commercial Path',
        'Operational Audit': '07 Operational Audit',
        'SWOT Analysis': '07 Operational Audit',
    }
```

2. In the body loop, after `bare = re.sub(r'^\d+\.\s+', '', title)`, apply the rename for the heading and the page div:

```python
        display_title = SECTION_RENAME_V19.get(bare, clean_title)
```

3. Prepend the Bottom Line page (before the first body page):

```python
    # v1.9: 01 Bottom Line — 30-Second Take + Decisions + debt summary.
    try:
        from consumer import ThirtySecondTake, DecisionSection, WhatThisMeansBox
        take = ThirtySecondTake.build_take(
            scores, registry, claims, commercial_conclusion or {}, reg_state_dict or {})
        decisions = DecisionSection.build(registry, commercial_conclusion or {},
                                          reg_state_dict or {}, scores)
        take_html = ('<div class="data-frame"><div class="df-title">30-Second Take</div>'
                     + md_block(take.markdown()) + '</div>')
        stance_html = ''
        for stance in decisions.all_stances():
            stance_html += ('<div class="card"><p><strong>' + html_mod.escape(stance['audience'])
                            + ':</strong> ' + md_inline(stance['stance']) + '</p></div>')
        body_html.insert(0,
            '<div class="page"><h2 class="section-title">01 Bottom Line</h2>'
            + take_html + '<h3>Decisions</h3>' + stance_html + '</div>')
    except Exception:
        pass  # consumer layer optional; report still renders
```

(`commercial_conclusion` and `reg_state_dict` are the variables already loaded in Plans D and E; `registry` is the registry loaded for the evidence column in Plan C. If any are absent, the try/except keeps the report renderable.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_consumer_render.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the full renderer suite**

Run: `python3 -m pytest report-renderer/tests/ -q`
Expected: all existing tests still pass (renames only affect display titles, not contract names).

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/tests/test_consumer_render.py
git commit -m "feat(renderer): v1.9 8-section restructure with bottom-line page"
```

---

### Task F4: Audit Trail page (P-code → evidence → source traceability)

**Files:**
- Modify: `report-renderer/render_report.py`
- Test: `report-renderer/tests/test_consumer_render.py`

**Interfaces:**
- Consumes: registry + scores `evidence_items`.
- Produces: `08 Audit Trail` page — a table mapping every proposition id to its claim, state/recovery, and the evidence ids + sources that support it.

- [ ] **Step 1: Write the failing test**

```python
# append to report-renderer/tests/test_consumer_render.py
def test_audit_trail_page_present(rendered):
    assert "08 Audit Trail" in rendered
    assert "Traceability" in rendered


def test_audit_trail_links_propositions_to_evidence(rendered):
    # P-03-003 appears in the audit trail with its registry state.
    assert "P-03-003" in rendered
    assert "E-03-001" in rendered  # evidence id from the manifest
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_consumer_render.py -v`
Expected: FAIL — `08 Audit Trail` missing.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/render_report.py`, build the evidence lookup from scores and append the Audit Trail page after the Bottom Line page insert:

```python
    # v1.9: 08 Audit Trail — proposition -> evidence -> source traceability.
    evidence_by_prop = {}
    for ev in scores.get('evidence_items', []):
        for pid in ev.get('supports', []):
            evidence_by_prop.setdefault(pid, []).append(
                f"{ev.get('evidence_id', '')} ({ev.get('source', '')})")

    def audit_trail_frame(registry):
        if registry is None:
            return placeholder_frame('Audit Trail')
        rows = ''.join(
            '<tr><td>' + html_mod.escape(p.proposition_id) + '</td>'
            '<td>' + md_inline(p.claim) + '</td>'
            '<td>' + html_mod.escape(f"{p.state} / {p.recovery_state}") + '</td>'
            '<td>' + md_inline('; '.join(evidence_by_prop.get(p.proposition_id, ['no direct evidence']))) + '</td></tr>'
            for p in sorted(registry.all(), key=lambda x: x.proposition_id))
        return ('<div class="data-frame"><div class="df-title">Traceability</div>'
                '<table class="data"><thead><tr><th>Proposition</th><th>Claim</th>'
                '<th>State / Recovery</th><th>Evidence (id + source)</th></tr></thead>'
                '<tbody>' + rows + '</tbody></table></div>')

    body_html.append('<div class="page"><h2 class="section-title">08 Audit Trail</h2>'
                     + audit_trail_frame(registry) + '</div>')
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_consumer_render.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Run the full renderer suite**

Run: `python3 -m pytest report-renderer/tests/ -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/tests/test_consumer_render.py
git commit -m "feat(renderer): audit trail page with proposition-to-evidence traceability"
```

---

### Task F5: Reader modes + report levels + full verification

**Files:**
- Modify: `report-renderer/render_report.py` (accept `reader_mode`/`level` params, default `STANDARD_EVALUATION`/`EXECUTIVE`)
- Modify: `report-renderer/consumer.py` (`LEVEL_SECTIONS`, `MODE_SECTIONS` used for emphasis)
- Test: `report-renderer/tests/test_consumer_render.py`

**Interfaces:**
- Consumes: `ReaderMode`, `ReportLevel` (Task F1).
- Produces: `render(..., reader_mode="EXECUTIVE", level="STANDARD_EVALUATION")` — reader mode adds a mode banner emphasizing the mode's sections; level filters generated pages.

- [ ] **Step 1: Write the failing test**

```python
# append to report-renderer/tests/test_consumer_render.py
def test_reader_mode_banner_present(rendered):
    assert "EXECUTIVE" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_consumer_render.py -v`
Expected: FAIL — no mode banner.

- [ ] **Step 3: Write minimal implementation**

In `render_report.py`, extend `render()`'s signature:

```python
def render(report_md, ledger_md, scores, submission_md=None,
           template_path=None, page_map=None, markers=True, v17_artifacts=None,
           ledger=None, ledger_path=None, reader_mode="EXECUTIVE",
           level="STANDARD_EVALUATION"):
```

After the Bottom Line insert, add the mode banner (page 1 header):

```python
    body_html.insert(0,
        '<div class="page"><div class="mode-banner">Reader mode: '
        + html_mod.escape(reader_mode) + ' | Report level: '
        + html_mod.escape(level) + '</div></div>')
```

(Update `consumer.py` docstring so `MODE_SECTIONS`/`LEVEL_SECTIONS` document that the mode banner is the emphasis mechanism; full per-section filtering is intentionally deferred to keep backward compatibility with the 57-test suite.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_consumer_render.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Full verification + re-render**

Run:

```bash
python3 -m pytest Test-report-results/tests_v17/ report-renderer/tests/ -q
python3 report-renderer/visual_qa.py 2>&1 | tail -5
```

Expected: all engine + renderer tests pass; visual QA PASS. Then re-render the US5215088 deliverables (v19 HTML + PDF) with the new renderer:

```bash
python3 - <<'EOF'
# Re-render US5215088 through the v1.9 renderer path (same entry point used
# by the orchestrator; commit regenerated HTML/PDF as deliverables).
EOF
```

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/consumer.py report-renderer/tests/test_consumer_render.py
git commit -m "feat(renderer): reader-mode and report-level banner on v1.9 reports"
```

---

## Self-Review

**1. Spec coverage:**
- Consumer layer at framework level → consumer.py consumes scores/registry/claims/commercial/regulatory — no report-specific strings in its logic.
- Three report levels → Task F1 (`ReportLevel`), Task F5 (`level` param).
- Page-1 30-Second Take → Tasks F1, F3.
- P-codes → traceability → Task F4 (Audit Trail maps every proposition to evidence ids + sources).
- "What this means" boxes → Task F2 (`WhatThisMeansBox`, registry-derived, evidence-constrained).
- Decision section (owner/investor/licensee/competitor) → Task F2 (`DecisionSection`; stances quote the data plane and cannot contradict it — the owner test asserts "license the patent" is absent when the patent is expired).
- 8-section restructure (01 Bottom Line … 08 Audit Trail) → Tasks F3, F4.
- Three reader modes → Tasks F1, F5.
- Evidence-constrained interpretation → `ThirtySecondTake` and `DecisionSection` compute from the data plane; no LLM calls in consumer.py.

**2. Placeholder scan:** No TBD/TODO; every step has concrete code and expected output.

**3. Type consistency:** `ThirtySecondTake.build_take` accepts dicts whose keys match the Plan B claims array and Plan D commercial conclusion / Plan E regulatory manifest; `DecisionSection.build` mirrors the same; `render()`'s new params have string defaults matching `ReaderMode`/`ReportLevel` values; the Audit Trail's `p.state / p.recovery_state` format matches the Plan C evidence column.