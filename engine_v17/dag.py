"""IEF Execution DAG — dependency graph for parallel lane dispatch.

The DAG is the single source of truth for which phases can run concurrently.
It is validated against skills/INDEX.md and schemas/skill_registry.json.

Autoprompt L1 coordinators consume launch groups derived from topological rank:
all phases whose hard dependencies are satisfied dispatch concurrently
(spawn-all-then-collect).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Canonical DAG derived from skills/INDEX.md + skill_registry.json
# ---------------------------------------------------------------------------

# Node = skill_id as in skill_registry.json (without the 'skill-' prefix)
# Edge: dependency -> dependent
DAG_NODES: tuple[str, ...] = (
    "gather-submission",      # 02
    "analyze-technology",     # 03
    "patent-landscape",       # 04
    "novelty-search",         # 05
    "literature-search",      # 06
    "market-opportunity",     # 07
    "identify-partners",      # 08
    "compile-report",         # 09
    "render-report",          # 10
)

# Hard dependency edges: (dependency, dependent)
DAG_EDGES_HARD: tuple[tuple[str, str], ...] = (
    ("gather-submission", "analyze-technology"),
    ("analyze-technology", "patent-landscape"),
    ("analyze-technology", "novelty-search"),
    ("analyze-technology", "literature-search"),
    ("analyze-technology", "market-opportunity"),
    ("patent-landscape", "novelty-search"),  # soft in registry but hard enough for DAG ordering when landscape is required
    ("market-opportunity", "identify-partners"),
    ("analyze-technology", "compile-report"),
    ("novelty-search", "compile-report"),
    ("literature-search", "compile-report"),
    ("market-opportunity", "compile-report"),
    ("identify-partners", "compile-report"),
    ("compile-report", "render-report"),
)

# Soft edges (do not block dispatch, but inform scheduling)
DAG_EDGES_SOFT: tuple[tuple[str, str], ...] = (
    ("patent-landscape", "novelty-search"),
    ("patent-landscape", "market-opportunity"),
)


@dataclass
class DagNode:
    skill_id: str
    phase: str  # e.g. "02", "03"
    hard_deps: list[str] = field(default_factory=list)
    soft_deps: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)

    @property
    def all_deps(self) -> list[str]:
        return self.hard_deps + self.soft_deps


# Phase mapping for sorting / reporting
PHASE_ORDER: dict[str, str] = {
    "gather-submission": "02",
    "analyze-technology": "03",
    "patent-landscape": "04",
    "novelty-search": "05",
    "literature-search": "06",
    "market-opportunity": "07",
    "identify-partners": "08",
    "compile-report": "09",
    "render-report": "10",
}


def build_dag(
    hard_edges: tuple[tuple[str, str], ...] = DAG_EDGES_HARD,
    soft_edges: tuple[tuple[str, str], ...] = DAG_EDGES_SOFT,
) -> dict[str, DagNode]:
    nodes: dict[str, DagNode] = {
        nid: DagNode(skill_id=nid, phase=PHASE_ORDER.get(nid, "00"))
        for nid in DAG_NODES
    }
    for dep, dependent in hard_edges:
        if dependent in nodes:
            nodes[dependent].hard_deps.append(dep)
        if dep in nodes:
            nodes[dep].blocks.append(dependent)
    for dep, dependent in soft_edges:
        if dependent in nodes and dep not in nodes[dependent].hard_deps:
            nodes[dependent].soft_deps.append(dep)
    return nodes


def topological_sort(dag: dict[str, DagNode]) -> list[str]:
    """Kahn's algorithm on hard edges only. Raises on cycle."""
    in_degree = {nid: len(node.hard_deps) for nid, node in dag.items()}
    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    result: list[str] = []
    while queue:
        queue.sort(key=lambda n: PHASE_ORDER.get(n, "99"))
        current = queue.pop(0)
        result.append(current)
        for node in dag.values():
            if current in node.hard_deps:
                in_degree[node.skill_id] -= 1
                if in_degree[node.skill_id] == 0:
                    queue.append(node.skill_id)
    if len(result) != len(dag):
        raise ValueError(f"DAG cycle detected: sorted {len(result)}/{len(dag)}")
    return result


def launch_groups(dag: dict[str, DagNode]) -> list[list[str]]:
    """Group nodes by topological rank for parallel dispatch.

    Each group contains all nodes whose hard dependencies are in earlier groups.
    Autoprompt dispatches each group via spawn-all-then-collect.
    """
    order = topological_sort(dag)
    # Compute rank = max rank of hard deps + 1
    rank: dict[str, int] = {}
    for nid in order:
        deps = dag[nid].hard_deps
        rank[nid] = (max(rank[d] for d in deps) + 1) if deps else 0
    max_rank = max(rank.values()) if rank else 0
    groups: list[list[str]] = [[] for _ in range(max_rank + 1)]
    for nid in order:
        groups[rank[nid]].append(nid)
    # Sort within group by phase order for determinism
    for g in groups:
        g.sort(key=lambda n: PHASE_ORDER.get(n, "99"))
    return groups


def validate_dag_against_registry(registry_path: Path | None = None) -> list[str]:
    """Check DAG nodes/edges are consistent with skill_registry.json. Returns errors."""
    if registry_path is None:
        registry_path = Path(__file__).parent.parent / "schemas" / "skill_registry.json"
    errors: list[str] = []
    if not registry_path.exists():
        return [f"registry not found: {registry_path}"]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry_ids = {s["skill_id"] for s in registry.get("skills", [])}
    dag_ids = set(DAG_NODES)
    if dag_ids - registry_ids:
        errors.append(f"DAG nodes not in registry: {dag_ids - registry_ids}")
    if registry_ids - dag_ids:
        # Allow extra nodes in registry that are not in DAG (e.g. future skills)
        pass
    # Check hard edges reference valid nodes
    for dep, dependent in DAG_EDGES_HARD:
        if dep not in dag_ids:
            errors.append(f"hard edge source not in DAG: {dep}")
        if dependent not in dag_ids:
            errors.append(f"hard edge target not in DAG: {dependent}")
    # Check no cycle
    try:
        topological_sort(build_dag())
    except ValueError as e:
        errors.append(str(e))
    return errors


def dag_to_execution_plan(
    required_domains: list[str],
    dag: dict[str, DagNode] | None = None,
) -> dict[str, Any]:
    """Slice the DAG to the mission's required_domains and produce launch groups.

    Returns a dict with: nodes, edges, launch_groups, topological_order
    """
    if dag is None:
        dag = build_dag()
    # Filter to required_domains + their hard transitive dependencies
    required_set = set(required_domains)
    # Add transitive hard dep closure
    changed = True
    while changed:
        changed = False
        for nid in list(required_set):
            for dep in dag[nid].hard_deps:
                if dep not in required_set:
                    required_set.add(dep)
                    changed = True
    # Build sliced DAG
    sliced = {nid: dag[nid] for nid in required_set if nid in dag}
    # Recompute hard deps within slice (drop deps outside slice)
    for nid, node in sliced.items():
        node_hard_in_slice = [d for d in node.hard_deps if d in sliced]
        # This mutates the node's deps for plan purposes; copy if needed downstream
        # We create a shallow copy dict to avoid mutating the canonical DAG
        pass
    # For launch grouping, use a filtered view
    filtered_nodes: dict[str, DagNode] = {}
    for nid in sliced:
        filtered_nodes[nid] = DagNode(
            skill_id=nid,
            phase=PHASE_ORDER.get(nid, "00"),
            hard_deps=[d for d in dag[nid].hard_deps if d in sliced],
            soft_deps=[d for d in dag[nid].soft_deps if d in sliced],
            blocks=[b for b in dag[nid].blocks if b in sliced],
        )
    try:
        order = topological_sort(filtered_nodes)
        groups = launch_groups(filtered_nodes)
    except ValueError as e:
        order = []
        groups = []
        raise ValueError(f"sliced DAG invalid: {e}") from e

    return {
        "nodes": {nid: {"phase": n.phase, "hard_deps": n.hard_deps, "soft_deps": n.soft_deps, "blocks": n.blocks} for nid, n in filtered_nodes.items()},
        "hard_edges": [(d, t) for d, t in DAG_EDGES_HARD if d in sliced and t in sliced],
        "soft_edges": [(d, t) for d, t in DAG_EDGES_SOFT if d in sliced and t in sliced],
        "topological_order": order,
        "launch_groups": groups,
        "required_domains": sorted(required_set),
    }


# ---------------------------------------------------------------------------
# Conceptual diagram for docs
# ---------------------------------------------------------------------------
DAG_DIAGRAM = """
    INTAKE (02 gather-submission)
       │
       ▼
    SOURCE VALIDATION + TECHNOLOGY (03 analyze-technology)
       │
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
    CLAIMS(05)         TECHNOLOGY(03)      MARKET(07)
       |                   |                   |
       v                   v                   v
    PRIOR ART(05)     LITERATURE(06)    COMPETITION(07)
       |                   |                   |
       +-------------------+-------------------+
                           │
                           v
                    EVIDENCE GRAPH
                           │
             +-------------+-------------+
             |             |             |
             v             v             v
          NOVELTY(05)  RIGHTS(graph) COMMERCIAL(07)
             |             |             |
             +-------------+-------------+
                           │
                           v
                  PROPOSITION AUDIT (09 compile)
                           │
                           v
                INDEPENDENT REVIEW (E7)
                           │
                           v
                 FRESH VERIFICATION (E8)
                           │
                           v
                      ARBITRATION
                           │
                           v
                    DECISION MODEL
                           │
                           v
                     REPORT RENDERER (10)
"""
