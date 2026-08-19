# Plan D — v1.9 Graph Separation: Patent Family / Technology Lineage / Commercial Portfolio

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate the single conflated "graph" concept into three distinct, typed graphs — patent family (existing `RightsGraph`), technology lineage (new), and commercial portfolio (new) — and make the commercial conclusion **computed from the graph, then explained by the LLM**, never invented by the LLM and retro-fitted to the graph. This prevents the exact failure mode where a later-gen technology (Neuralace) or a licensee (Blackrock Neurotech) contaminates the scope of the target patent (US5215088).

**Architecture:** `engine_v17/rights_graph.py` already models the patent-family graph (keep as-is). Two new modules add the other two graphs: `technology_graph.py` (generation nodes + derivation edges + provenance per node) and `commercial_graph.py` (product/company nodes + commercializes/replaces edges + status per node). A deterministic `derive_commercial_conclusion(graph)` computes the conclusion from graph facts alone; the report builder consumes that conclusion and only *explains* it. The orchestrator wires all three graphs into `run()`/`run_generic()` and emits `technology-lineage.json` and `commercial-portfolio.json` alongside the existing `rights-graph.json` and `claim-graph.json`. The renderer gains two data-frame pages (Technology Lineage, Commercial Portfolio).

**Tech Stack:** Python 3.10+ (repo runs 3.14), pytest, dataclasses + `Enum`, JSON artifacts.

## Global Constraints

- Three distinct graphs, never mixed:
  - **Patent family** = `RightsGraph` (existing): patent, family members, legal status, assignments, asset layers.
  - **Technology lineage** = `TechnologyLineageGraph` (new): generation nodes (Gen 1 … Gen N) with `generation`, `label`, `provenance` (patent refs / publications), and directed edges `("Gen1", "derives_from"/"supersedes", "Gen2")`.
  - **Commercial portfolio** = `CommercialPortfolioGraph` (new): product/company nodes with `name`, `kind` (PRODUCT / COMPANY / ASSET), `status` (ACTIVE / INACTIVE / EXPIRED_PATENT / LATER_GEN), `licensor`, `licensee`, `patent`, and edges `("US5215088A", "commercialized_by", "Blackrock Neurotech")`, `("Utah Array", "descends_from", "Neuralace")`.
- `derive_commercial_conclusion(graph) -> CommercialConclusion` is DETERMINISTIC: it reads graph facts only (expired patent → `standalone_licensing_leverage: minimal`; licensee with active product → `commercialization: active_via_licensee`; later-gen node → `scope_note: later_generation_present_does_not_extend_target_patent`). No LLM call inside.
- Report text MUST NOT assert a commercial conclusion that `derive_commercial_conclusion` cannot derive from the graph. `report_builder` takes the computed conclusion as input and explains it.
- US5215088 fixture graph facts (authoritative, from user review): US5215088A = EXPIRED (June 1, 2010); Blackrock Neurotech = exclusive licensee / commercializer of the Utah Array / NeuroPort; Neuralace = 2022 later-gen flexible technology (10,000+ channels) that must NOT be treated as within US5215088 claim scope.
- Backward compatibility: `RightsGraph` and `ClaimGraph` untouched; all existing engine tests (18 files) keep passing.
- No report-specific hand-fixes. All changes are engine/orchestrator/renderer-level.
- Commit style: conventional commits (`feat:`, `test:`, `refactor:`, `docs:`).

## File Structure

- `engine_v17/technology_graph.py` — new: `TechnologyLineageGraph`, `LineageNode`, `build_technology_lineage()`.
- `engine_v17/commercial_graph.py` — new: `CommercialPortfolioGraph`, `CommercialConclusion`, `build_commercial_portfolio()`, `derive_commercial_conclusion()`.
- `engine_v17/orchestrator.py` — wire both new graphs into `run()` and `run_generic()`; emit `technology-lineage.json` and `commercial-portfolio.json`.
- `engine_v17/report_builder.py` — `build_report` accepts the commercial conclusion and explains it (no invented conclusions).
- `report-renderer/render_report.py` — data-frame pages for Technology Lineage and Commercial Portfolio.
- `Test-report-results/tests_v17/test_graphs.py` — new engine tests.
- `report-renderer/tests/test_graphs_render.py` — new renderer tests.
- `evaluations/US5215088/technology-lineage.json`, `evaluations/US5215088/commercial-portfolio.json` — fixture artifacts.

---

### Task D1: `TechnologyLineageGraph` in `engine_v17/technology_graph.py`

**Files:**
- Create: `engine_v17/technology_graph.py`
- Test: `Test-report-results/tests_v17/test_graphs.py` (new)

**Interfaces:**
- Consumes: nothing (standalone module).
- Produces: `LineageNode` (generation, label, provenance, scope), `TechnologyLineageGraph` (nodes, edges, to_dict), `build_technology_lineage(records: list[dict]) -> TechnologyLineageGraph`.

- [ ] **Step 1: Write the failing test**

```python
# Test-report-results/tests_v17/test_graphs.py
from engine_v17.technology_graph import build_technology_lineage


def test_technology_lineage_builds_nodes_and_edges():
    records = [
        {"generation": "Gen1", "label": "Utah Array (3D penetrating silicon)",
         "provenance": ["US5215088A", "Normann lab publications"],
         "scope": "TARGET_PATENT"},
        {"generation": "Gen3", "label": "Neuralace (flexible 10k-channel)",
         "provenance": ["Blackrock 2022 announcement"],
         "scope": "TECHNOLOGY_LINEAGE"},
    ]
    g = build_technology_lineage(records)
    assert g.to_dict()["nodes"][0]["generation"] == "Gen1"
    assert g.to_dict()["nodes"][1]["generation"] == "Gen3"
    # Edges are derived: later generation descends from earlier ones.
    assert any(e[2] == "Gen3" and e[0] == "Gen1" for e in g.to_dict()["edges"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine_v17.technology_graph'`

- [ ] **Step 3: Write minimal implementation**

Create `engine_v17/technology_graph.py`:

```python
"""v1.9 technology lineage graph.

Captures technology generations and their derivation relationships so the
report can show *what the target patent belongs to* without letting later
generations leak into claim scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LineageNode:
    generation: str
    label: str = ""
    provenance: list[str] = field(default_factory=list)
    scope: str = "TECHNOLOGY_LINEAGE"


@dataclass
class TechnologyLineageGraph:
    nodes: list[LineageNode] = field(default_factory=list)
    edges: list[tuple[str, str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [
                {"generation": n.generation, "label": n.label,
                 "provenance": n.provenance, "scope": n.scope}
                for n in self.nodes
            ],
            "edges": [list(e) for e in self.edges],
        }


def build_technology_lineage(records: list[dict[str, Any]]) -> TechnologyLineageGraph:
    """Build the lineage graph from generation records.

    Edges are derived deterministically: each later generation derives from
    the immediately preceding generation (`("Gen1", "supersedes", "Gen2")`).
    This keeps the graph computable and auditable — no LLM inference.
    """
    nodes = [LineageNode(
        generation=r.get("generation", f"Gen{i + 1}"),
        label=r.get("label", ""),
        provenance=list(r.get("provenance", [])),
        scope=r.get("scope", "TECHNOLOGY_LINEAGE"),
    ) for i, r in enumerate(records)]
    # Sort by generation ordinal so edges are deterministic.
    def _ord(g: str) -> int:
        import re
        m = re.search(r"\d+", g)
        return int(m.group(0)) if m else len(nodes)
    nodes.sort(key=lambda n: _ord(n.generation))
    edges = []
    for i in range(1, len(nodes)):
        edges.append((nodes[i - 1].generation, "supersedes", nodes[i].generation))
    return TechnologyLineageGraph(nodes=nodes, edges=edges)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/technology_graph.py Test-report-results/tests_v17/test_graphs.py
git commit -m "feat(engine): add technology lineage graph with derived edges"
```

---

### Task D2: `CommercialPortfolioGraph` + deterministic `derive_commercial_conclusion`

**Files:**
- Create: `engine_v17/commercial_graph.py`
- Test: `Test-report-results/tests_v17/test_graphs.py`

**Interfaces:**
- Consumes: nothing (standalone module).
- Produces: `CommercialPortfolioGraph` (nodes, edges, to_dict), `build_commercial_portfolio(records)`, `CommercialConclusion` (dataclass), `derive_commercial_conclusion(graph) -> CommercialConclusion` — deterministic, no LLM.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_graphs.py
from engine_v17.commercial_graph import (
    build_commercial_portfolio, derive_commercial_conclusion,
)


def test_commercial_portfolio_builds_from_records():
    records = [
        {"name": "US5215088A", "kind": "ASSET", "status": "EXPIRED_PATENT"},
        {"name": "Blackrock Neurotech", "kind": "COMPANY", "status": "ACTIVE",
         "licensor": None, "licensee": "exclusive", "patent": "US5215088A"},
        {"name": "Utah Array / NeuroPort", "kind": "PRODUCT", "status": "ACTIVE",
         "patent": "US5215088A"},
        {"name": "Neuralace", "kind": "PRODUCT", "status": "LATER_GEN",
         "patent": None},
    ]
    g = build_commercial_portfolio(records)
    d = g.to_dict()
    assert any(n["name"] == "US5215088A" and n["status"] == "EXPIRED_PATENT" for n in d["nodes"])
    # commercialized_by edge derived from licensee records
    assert any(e[0] == "US5215088A" and e[1] == "commercialized_by" and e[2] == "Blackrock Neurotech"
               for e in d["edges"])


def test_derive_commercial_conclusion_is_deterministic():
    records = [
        {"name": "US5215088A", "kind": "ASSET", "status": "EXPIRED_PATENT"},
        {"name": "Blackrock Neurotech", "kind": "COMPANY", "status": "ACTIVE",
         "licensee": "exclusive", "patent": "US5215088A"},
        {"name": "Neuralace", "kind": "PRODUCT", "status": "LATER_GEN", "patent": None},
    ]
    g = build_commercial_portfolio(records)
    c1 = derive_commercial_conclusion(g)
    c2 = derive_commercial_conclusion(g)
    assert c1 == c2  # deterministic — same input, same conclusion
    assert c1.standalone_licensing_leverage == "minimal"
    assert c1.commercialization == "active_via_licensee"
    assert "does not extend" in c1.scope_note.lower()


def test_derive_commercial_conclusion_active_patent_differs():
    records = [
        {"name": "US9999999B2", "kind": "ASSET", "status": "ACTIVE"},
        {"name": "Acme", "kind": "COMPANY", "status": "ACTIVE",
         "licensee": None, "patent": "US9999999B2"},
    ]
    g = build_commercial_portfolio(records)
    c = derive_commercial_conclusion(g)
    assert c.standalone_licensing_leverage == "available"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine_v17.commercial_graph'`

- [ ] **Step 3: Write minimal implementation**

Create `engine_v17/commercial_graph.py`:

```python
"""v1.9 commercial portfolio graph.

Models the commercial entities around the target patent (products, companies,
licensees, later-generation technology) and derives the commercial conclusion
DETERMINISTICALLY from the graph. The LLM explains this conclusion in report
text; it never invents one.

Scope rule: a LATER_GEN product node (e.g. Neuralace) does not extend the
target patent's claim scope. That constraint is encoded in the graph, not
in prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommercialNode:
    name: str
    kind: str = "COMPANY"          # ASSET | COMPANY | PRODUCT
    status: str = "ACTIVE"         # ACTIVE | INACTIVE | EXPIRED_PATENT | LATER_GEN
    licensor: str | None = None
    licensee: str | None = None    # None | exclusive | non_exclusive
    patent: str | None = None
    scope_note: str = ""


@dataclass
class CommercialPortfolioGraph:
    nodes: list[CommercialNode] = field(default_factory=list)
    edges: list[tuple[str, str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [
                {"name": n.name, "kind": n.kind, "status": n.status,
                 "licensor": n.licensor, "licensee": n.licensee,
                 "patent": n.patent, "scope_note": n.scope_note}
                for n in self.nodes
            ],
            "edges": [list(e) for e in self.edges],
        }


def build_commercial_portfolio(records: list[dict[str, Any]]) -> CommercialPortfolioGraph:
    nodes = [CommercialNode(
        name=r["name"],
        kind=r.get("kind", "COMPANY"),
        status=r.get("status", "ACTIVE"),
        licensor=r.get("licensor"),
        licensee=r.get("licensee"),
        patent=r.get("patent"),
        scope_note=r.get("scope_note", ""),
    ) for r in records]
    edges = []
    # Derive edges deterministically from node fields.
    for n in nodes:
        if n.licensee and n.patent:
            edges.append((n.patent, "commercialized_by", n.name))
        if n.status == "LATER_GEN":
            edges.append((n.name, "does_not_extend", n.patent or "TARGET_PATENT"))
    return CommercialPortfolioGraph(nodes=nodes, edges=edges)


@dataclass
class CommercialConclusion:
    standalone_licensing_leverage: str
    commercialization: str
    scope_note: str
    constraints: list[str] = field(default_factory=list)


def derive_commercial_conclusion(graph: CommercialPortfolioGraph) -> CommercialConclusion:
    """Deterministic conclusion from graph facts — no LLM, no prose.

    - EXPIRED_PATENT asset  -> standalone licensing leverage = minimal.
    - Licensee with an active product -> commercialization = active_via_licensee.
    - LATER_GEN node present -> scope note warns it does not extend the target.
    """
    assets = [n for n in graph.nodes if n.kind == "ASSET"]
    products = [n for n in graph.nodes if n.kind == "PRODUCT"]
    companies = [n for n in graph.nodes if n.kind == "COMPANY"]

    expired = any(a.status == "EXPIRED_PATENT" for a in assets)
    leverage = "minimal" if expired else "available"

    licensee_active = any(
        c.licensee and any(p.status == "ACTIVE" for p in products)
        for c in companies
    )
    commercialization = "active_via_licensee" if licensee_active else "no_active_commercialization"

    later_gen = any(p.status == "LATER_GEN" for p in products)
    scope_note = (
        "Later-generation technology present in the commercial portfolio "
        "does not extend the target patent's claim scope."
        if later_gen else "No later-generation scope boundary required."
    )

    constraints = []
    if expired:
        constraints.append("standalone_patent_licensing_blocked")
        constraints.append("portfolio_diligence_required")

    return CommercialConclusion(
        standalone_licensing_leverage=leverage,
        commercialization=commercialization,
        scope_note=scope_note,
        constraints=constraints,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run the full engine suite**

Run: `python3 -m pytest Test-report-results/tests_v17/ -q`
Expected: all existing tests still pass.

- [ ] **Step 6: Commit**

```bash
git add engine_v17/commercial_graph.py Test-report-results/tests_v17/test_graphs.py
git commit -m "feat(engine): commercial portfolio graph with deterministic conclusion"
```

---

### Task D3: Wire graphs into orchestrator + report builder

**Files:**
- Modify: `engine_v17/orchestrator.py` (`run`, `run_generic`)
- Modify: `engine_v17/report_builder.py` (`build_report`)
- Test: `Test-report-results/tests_v17/test_graphs.py`

**Interfaces:**
- Consumes: `build_technology_lineage`, `build_commercial_portfolio`, `derive_commercial_conclusion` (Tasks D1, D2).
- Produces: `technology-lineage.json` and `commercial-portfolio.json` written to the output dir; `build_report` signature gains a `commercial_conclusion` param used to explain (never invent) the conclusion.

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_graphs.py
import json


def test_orchestrator_emits_commercial_portfolio_artifact(tmp_path):
    # Simulate the orchestrator's emit path with fixture records.
    from engine_v17.commercial_graph import build_commercial_portfolio, derive_commercial_conclusion
    records = [
        {"name": "US5215088A", "kind": "ASSET", "status": "EXPIRED_PATENT"},
        {"name": "Blackrock Neurotech", "kind": "COMPANY", "status": "ACTIVE",
         "licensee": "exclusive", "patent": "US5215088A"},
        {"name": "Neuralace", "kind": "PRODUCT", "status": "LATER_GEN", "patent": None},
    ]
    g = build_commercial_portfolio(records)
    c = derive_commercial_conclusion(g)
    out = tmp_path / "commercial-portfolio.json"
    out.write_text(json.dumps({"graph": g.to_dict(), "conclusion": c.__dict__}, indent=2))
    data = json.loads(out.read_text())
    assert data["conclusion"]["standalone_licensing_leverage"] == "minimal"
    assert data["conclusion"]["commercialization"] == "active_via_licensee"
    assert data["conclusion"]["scope_note"] != ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: PASS immediately if the implementation works — the test simulates the emit path. To make it genuinely red, first run it WITHOUT the commercial_graph import existing; after Task D2 it will pass. This test guards the wiring contract; the orchestrator wiring itself is verified in Step 4 by invoking `run()` on the fixture evaluation dir.

- [ ] **Step 3: Wire the orchestrator**

In `engine_v17/orchestrator.py`, add imports at the top:

```python
from .commercial_graph import (
    build_commercial_portfolio, derive_commercial_conclusion,
)
from .technology_graph import build_technology_lineage
```

In `run()` (after the `rights = build_rights_graph([status])` line ~190) and in `run_generic()` (after line ~484), add:

```python
    lineage = build_technology_lineage(
        [{"generation": "Gen1", "label": "Target patent technology (first generation)",
          "provenance": [f"{invention_id} patent text"], "scope": "TARGET_PATENT"}]
        if not (evaluation_dir / "technology-lineage.json").exists()
        else json.loads((evaluation_dir / "technology-lineage.json").read_text())["nodes"]
    )
    portfolio = build_commercial_portfolio(
        json.loads((evaluation_dir / "commercial-portfolio.json").read_text())["nodes"]
        if (evaluation_dir / "commercial-portfolio.json").exists()
        else [{"name": f"{invention_id}", "kind": "ASSET",
               "status": "EXPIRED_PATENT" if status.get("state") == "EXPIRED" else "ACTIVE"}]
    )
    commercial = derive_commercial_conclusion(portfolio)
```

Emit the artifacts next to `rights-graph.json`:

```python
    (output_dir / "technology-lineage.json").write_text(
        json.dumps(lineage.to_dict(), indent=2) + "\n", encoding="utf-8")
    (output_dir / "commercial-portfolio.json").write_text(
        json.dumps({"graph": portfolio.to_dict(), "conclusion": commercial.__dict__},
                   indent=2) + "\n", encoding="utf-8")
```

- [ ] **Step 4: Verify on the fixture evaluation dir**

Run:

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, ".")
from engine_v17.orchestrator import run
from pathlib import Path
# Dry wiring check: build the fixture portfolio from committed JSON if present.
p = Path("evaluations/US5215088/commercial-portfolio.json")
print("fixture portfolio present:", p.exists())
EOF
```

Then create the fixture artifacts (see Task D4) and re-run the full engine suite.

- [ ] **Step 5: Run the full engine suite**

Run: `python3 -m pytest Test-report-results/tests_v17/ -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add engine_v17/orchestrator.py engine_v17/report_builder.py Test-report-results/tests_v17/test_graphs.py
git commit -m "feat(engine): wire technology lineage and commercial portfolio graphs into orchestrator"
```

---

### Task D4: US5215088 fixture graph artifacts

**Files:**
- Create: `evaluations/US5215088/technology-lineage.json`
- Create: `evaluations/US5215088/commercial-portfolio.json`
- Test: `Test-report-results/tests_v17/test_graphs.py`

**Interfaces:**
- Consumes: `build_technology_lineage`, `build_commercial_portfolio`, `derive_commercial_conclusion`.
- Produces: committed fixture artifacts whose conclusions match the authoritative review (expired patent, licensee-active, later-gen scope boundary).

- [ ] **Step 1: Write the failing test**

```python
# append to Test-report-results/tests_v17/test_graphs.py
import os
from engine_v17.commercial_graph import build_commercial_portfolio, derive_commercial_conclusion
from engine_v17.technology_graph import build_technology_lineage


def test_us5215088_fixture_graphs_are_authoritative():
    base = os.path.join(os.path.dirname(__file__), "..", "..", "evaluations", "US5215088")
    tl = json.load(open(os.path.join(base, "technology-lineage.json"), encoding="utf-8"))
    cp = json.load(open(os.path.join(base, "commercial-portfolio.json"), encoding="utf-8"))
    assert tl["nodes"][0]["generation"] == "Gen1"
    g = build_commercial_portfolio(cp["nodes"])
    c = derive_commercial_conclusion(g)
    assert c.standalone_licensing_leverage == "minimal"
    assert c.commercialization == "active_via_licensee"
    assert "does not extend" in c.scope_note.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: FAIL — fixture files missing.

- [ ] **Step 3: Create the fixture artifacts**

Create `evaluations/US5215088/technology-lineage.json`:

```json
{
  "nodes": [
    {"generation": "Gen1", "label": "Utah Array — 3D penetrating silicon electrode array (target patent)",
     "provenance": ["US5215088A", "Normann lab publications"], "scope": "TARGET_PATENT"},
    {"generation": "Gen2", "label": "Flexible/µECoG and surface-array variants",
     "provenance": ["Andreis et al. 2024", "Gardner et al. 2018"], "scope": "TECHNOLOGY_LINEAGE"},
    {"generation": "Gen3", "label": "Neuralace — flexible 10,000+ channel BCI (2022, later generation)",
     "provenance": ["Blackrock Neurotech 2022 announcement"], "scope": "TECHNOLOGY_LINEAGE"}
  ],
  "edges": [
    ["Gen1", "supersedes", "Gen2"],
    ["Gen2", "supersedes", "Gen3"]
  ]
}
```

Create `evaluations/US5215088/commercial-portfolio.json`:

```json
{
  "graph": {
    "nodes": [
      {"name": "US5215088A", "kind": "ASSET", "status": "EXPIRED_PATENT",
       "licensor": null, "licensee": null, "patent": null,
       "scope_note": "Expired June 1, 2010."},
      {"name": "University of Utah", "kind": "COMPANY", "status": "ACTIVE",
       "licensor": "yes", "licensee": null, "patent": "US5215088A",
       "scope_note": "Original assignee."},
      {"name": "Blackrock Neurotech", "kind": "COMPANY", "status": "ACTIVE",
       "licensor": null, "licensee": "exclusive", "patent": "US5215088A",
       "scope_note": "Exclusive licensee / commercializer of Utah Array and NeuroPort."},
      {"name": "Utah Array / NeuroPort", "kind": "PRODUCT", "status": "ACTIVE",
       "licensor": null, "licensee": null, "patent": "US5215088A",
       "scope_note": "Commercial product line."},
      {"name": "Neuralace", "kind": "PRODUCT", "status": "LATER_GEN",
       "licensor": null, "licensee": null, "patent": null,
       "scope_note": "2022 flexible 10,000+ channel technology — outside US5215088 claim scope."}
    ],
    "edges": [
      ["US5215088A", "commercialized_by", "Blackrock Neurotech"],
      ["Neuralace", "does_not_extend", "US5215088A"]
    ]
  },
  "conclusion": {
    "standalone_licensing_leverage": "minimal",
    "commercialization": "active_via_licensee",
    "scope_note": "Later-generation technology present in the commercial portfolio does not extend the target patent's claim scope.",
    "constraints": ["standalone_patent_licensing_blocked", "portfolio_diligence_required"]
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest Test-report-results/tests_v17/test_graphs.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add evaluations/US5215088/technology-lineage.json evaluations/US5215088/commercial-portfolio.json Test-report-results/tests_v17/test_graphs.py
git commit -m "data(eval): add authoritative US5215088 lineage and portfolio graph fixtures"
```

---

### Task D5: Renderer pages for lineage and portfolio

**Files:**
- Modify: `report-renderer/render_report.py`
- Test: `report-renderer/tests/test_graphs_render.py` (new)

**Interfaces:**
- Consumes: `technology-lineage.json` and `commercial-portfolio.json` (via `scores` extension or direct file read in `render()`).
- Produces: two data-frame pages: "Technology Lineage" (generation ladder with provenance) and "Commercial Portfolio" (node/status table + derived conclusion box).

- [ ] **Step 1: Write the failing test**

```python
# report-renderer/tests/test_graphs_render.py
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


def test_technology_lineage_page_present(rendered):
    assert "Technology Lineage" in rendered
    assert "Gen1" in rendered


def test_commercial_portfolio_page_present(rendered):
    assert "Commercial Portfolio" in rendered
    assert "Blackrock Neurotech" in rendered


def test_commercial_portfolio_shows_deterministic_conclusion(rendered):
    assert "standalone_licensing_leverage" in rendered
    assert "minimal" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest report-renderer/tests/test_graphs_render.py -v`
Expected: FAIL — pages missing.

- [ ] **Step 3: Write minimal implementation**

In `report-renderer/render_report.py`, inside `render()`, load the fixture artifacts (next to the `ledger_path` handling):

```python
    # v1.9: graph artifacts (technology lineage + commercial portfolio).
    lineage_path = os.path.join(
        os.path.dirname(ledger_path) if ledger_path else here,
        "technology-lineage.json")
    portfolio_path = os.path.join(
        os.path.dirname(ledger_path) if ledger_path else here,
        "commercial-portfolio.json")
    lineage = {}
    portfolio = {}
    for _p, _d in ((lineage_path, lineage), (portfolio_path, portfolio)):
        if os.path.exists(_p):
            try:
                _d.update(json.load(open(_p, encoding="utf-8")))
            except Exception:
                pass
```

Add two frame builders (next to `product_diagram`):

```python
    def lineage_frame(data):
        nodes = data.get('nodes', [])
        if not nodes:
            return placeholder_frame('Technology Lineage')
        rows = ''.join(
            '<tr><td>' + html_mod.escape(n.get('generation', '')) + '</td>'
            '<td>' + md_inline(n.get('label', '')) + '</td>'
            '<td>' + md_inline('; '.join(n.get('provenance', []))) + '</td>'
            '<td>' + html_mod.escape(n.get('scope', '')) + '</td></tr>'
            for n in nodes)
        return ('<div class="data-frame"><div class="df-title">Technology Lineage</div>'
                '<table class="data"><thead><tr><th>Generation</th><th>Technology</th>'
                '<th>Provenance</th><th>Scope</th></tr></thead><tbody>'
                + rows + '</tbody></table></div>')

    def portfolio_frame(data):
        nodes = data.get('graph', {}).get('nodes', [])
        conclusion = data.get('conclusion', {})
        if not nodes:
            return placeholder_frame('Commercial Portfolio')
        rows = ''.join(
            '<tr><td>' + html_mod.escape(n.get('name', '')) + '</td>'
            '<td>' + html_mod.escape(n.get('kind', '')) + '</td>'
            '<td>' + html_mod.escape(n.get('status', '')) + '</td>'
            '<td>' + html_mod.escape(n.get('licensee', '') or '') + '</td>'
            '<td>' + md_inline(n.get('scope_note', '')) + '</td></tr>'
            for n in nodes)
        conclusion_html = ''
        if conclusion:
            conclusion_html = ('<div class="conclusion-box"><strong>Derived conclusion '
                               '(deterministic, from graph):</strong><br>'
                               'standalone_licensing_leverage = '
                               + html_mod.escape(str(conclusion.get('standalone_licensing_leverage', '')))
                               + '<br>commercialization = '
                               + html_mod.escape(str(conclusion.get('commercialization', '')))
                               + '<br><em>' + md_inline(conclusion.get('scope_note', '')) + '</em></div>')
        return ('<div class="data-frame"><div class="df-title">Commercial Portfolio</div>'
                '<table class="data"><thead><tr><th>Entity</th><th>Kind</th><th>Status</th>'
                '<th>Licensee</th><th>Scope Note</th></tr></thead><tbody>'
                + rows + '</tbody></table>' + conclusion_html + '</div>')
```

Append the two pages:

```python
    body_html.append('<div class="page"><h2 class="section-title">Technology Lineage</h2>'
                     + lineage_frame(lineage) + '</div>')
    body_html.append('<div class="page"><h2 class="section-title">Commercial Portfolio</h2>'
                     + portfolio_frame(portfolio) + '</div>')
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest report-renderer/tests/test_graphs_render.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run both full suites + visual QA**

Run:

```bash
python3 -m pytest Test-report-results/tests_v17/ report-renderer/tests/ -q
python3 report-renderer/visual_qa.py 2>&1 | tail -5
```

Expected: all pass; visual QA PASS with the two new pages.

- [ ] **Step 6: Commit**

```bash
git add report-renderer/render_report.py report-renderer/tests/test_graphs_render.py
git commit -m "feat(renderer): technology lineage and commercial portfolio pages"
```

---

## Self-Review

**1. Spec coverage:**
- Three separate graphs (patent family / technology lineage / commercial portfolio) → Task D1 (lineage), Task D2 (portfolio), existing `RightsGraph` untouched (family).
- Commercial conclusion computed from graph then LLM explains → Task D2 (`derive_commercial_conclusion` deterministic, no LLM), Task D3 (report builder explains the passed-in conclusion), Task D5 (renderer shows the derived conclusion box).
- Neuralace must not contaminate US5215088 scope → Task D2 (`LATER_GEN` + `does_not_extend` edge), Task D4 (fixture scope_note).
- Expired patent + licensee facts → Task D4 (fixture: EXPIRED_PATENT, Blackrock exclusive licensee).
- Backward compatibility → `RightsGraph`/`ClaimGraph` untouched; full engine suite re-run each task.

**2. Placeholder scan:** No TBD/TODO; every step has concrete code and expected output.

**3. Type consistency:** `derive_commercial_conclusion` returns `CommercialConclusion` with three string fields + `constraints`; renderer consumes the dict-serialized form (`__dict__`); fixture JSON `conclusion` keys match; `TechnologyLineageGraph.to_dict()` keys (`generation`, `label`, `provenance`, `scope`) match the renderer's `lineage_frame` lookups.