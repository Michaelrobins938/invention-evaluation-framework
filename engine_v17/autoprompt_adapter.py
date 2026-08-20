"""Adapter layer between Autoprompt execution OS and IEF domain/evidence layer.

Conceptually:

    Autoprompt Mission
          │
          ▼
    IEF Mission Adapter  (this file)
          │
          ▼
    IEF Evaluation Mission

and:

    IEF Skill Result
          │
          ▼
    Autoprompt Result Adapter (this file)
          │
          ▼
    Autoprompt Execution Ledger

Keeps adapters small, typed/validated, and documented. No recursive orchestration.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .dag import dag_to_execution_plan, build_dag, validate_dag_against_registry, DAG_DIAGRAM
from .evidence_gate import apply_evidence_sufficiency_gate, SourceObject
from .execution import ExecutionLedger, create_run_manifest
from .mission import EvaluationMission, create_mission
from .status import CombinedStatus, ExecutionStatus, EvidenceStatus


# ---------------------------------------------------------------------------
# Autoprompt Mission → IEF Evaluation Mission
# ---------------------------------------------------------------------------

def adapt_autoprompt_mission_to_ief(
    autoprompt_mission_text: str,
    evaluation_id: str,
    target: str,
    evaluation_dir: str | Path,
    scope: str = "full-pipeline",
    framework_version: str = "v1.7",
    execution_version: str = "autoprompt-1.0.3-opencode",
    **kwargs: Any,
) -> EvaluationMission:
    """Translate a raw Autoprompt mission string into a typed IEF EvaluationMission.

    The Autoprompt mission text is the immutable source; this adapter derives the
    IEF mission without redefining it. Workers may not redefine the global mission.
    """
    mission = create_mission(
        evaluation_id=evaluation_id,
        target=target,
        mission_text=autoprompt_mission_text,
        scope=scope,
        evaluation_dir=evaluation_dir,
        framework_version=framework_version,
        execution_version=execution_version,
        **kwargs,
    )
    errors = mission.validate()
    if errors:
        raise ValueError(f"mission validation failed: {errors}")
    return mission


def autoprompt_result_to_ledger(
    skill_id: str,
    skill_result: dict[str, Any],
    ledger: ExecutionLedger,
    phase_id: str | None = None,
) -> dict[str, Any]:
    """Translate an IEF skill result into an Autoprompt execution ledger entry.

    The skill result must contain structured observations/propositions/evidence
    references — arbitrary prose is not authoritative evidence.
    """
    from .execution import PHASE_COVERAGE_GATE
    # Map skill_id to phase_id
    if phase_id is None:
        skill_to_phase = {
            "gather-submission": "02",
            "analyze-technology": "03",
            "patent-landscape": "04",
            "novelty-search": "05",
            "literature-search": "04",  # literature shares 04 lane group logically but kept separate
            "market-opportunity": "06",
            "identify-partners": "07",
            "compile-report": "08",
            "render-report": "09",
        }
        phase_id = skill_to_phase.get(skill_id, "00")

    # Evidence-sufficiency check on the result's evidence references
    evidence_refs = skill_result.get("evidence_refs", [])
    has_structured_evidence = bool(evidence_refs) or skill_result.get("evidence_sufficiency_passed", False)
    outcome = skill_result.get("outcome", "completed")
    if not has_structured_evidence and skill_result.get("requires_evidence", False):
        outcome = "evidence insufficient — result not authoritative for findings"

    record = ledger.record(
        phase_id=phase_id,
        action_type=skill_id,
        source=skill_result.get("source", "ief-domain-skill"),
        query=skill_result.get("query", skill_id),
        result_count=skill_result.get("result_count"),
        result_artifact=skill_result.get("result_artifact"),
        outcome=outcome,
        candidate_evidence=has_structured_evidence,
        evidence_sufficiency=skill_result.get("evidence_sufficiency_passed", False),
    )
    return record.to_dict()


# ---------------------------------------------------------------------------
# Execution plan builder (mission → DAG → Autoprompt lanes)
# ---------------------------------------------------------------------------

def build_execution_plan(mission: EvaluationMission) -> dict[str, Any]:
    """Build the complete execution plan consumed by Autoprompt L1 coordinators.

    Validates the DAG, slices it to the mission's required_domains, and
    computes launch groups for spawn-all-then-collect dispatch.
    """
    dag_errors = validate_dag_against_registry()
    if dag_errors:
        raise ValueError(f"DAG validation failed: {dag_errors}")

    dag = build_dag()
    plan = dag_to_execution_plan(mission.required_domains, dag)
    plan["mission"] = mission.to_dict()
    plan["diagram"] = DAG_DIAGRAM
    plan["contract_ref"] = "IEF_EXECUTION_CONTRACT.md"
    return plan


# ---------------------------------------------------------------------------
# Unified run manifest adapter
# ---------------------------------------------------------------------------

def create_unified_run_manifest(
    mission: EvaluationMission,
    evaluation_dir: Path,
) -> dict[str, Any]:
    """Create the canonical run manifest that unifies Autoprompt + IEF state.

    Answers: what mission, which framework/Autoprompt/model, which skills/agents,
    dependencies, evidence, propositions, gates, arbitration, final statuses.
    """
    manifest = create_run_manifest(
        mission.evaluation_id,
        evaluation_dir,
        pipeline_version=mission.framework_version,
    )
    manifest["execution_version"] = mission.execution_version
    manifest["mission"] = mission.to_dict()
    manifest["autoprompt"] = {
        "provider": "opencode",
        "version": mission.execution_version,
        "concurrency": mission.constraints.get("concurrency", "tokensaver"),
        "effort": "inherited-only",
    }
    manifest["dag"] = dag_to_execution_plan(mission.required_domains)
    return manifest


def write_execution_plan(plan: dict[str, Any], evaluation_dir: Path) -> Path:
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    path = evaluation_dir / "execution-plan.json"
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return path
