"""Compile v1.7 graph state into report-facing artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .constraints import calculate_evidence_debt, propagate_constraints
from .coverage import (
    ALL_GATES,
    CoverageReport,
    run_all_coverage_gates,
)
from .execution import ExecutionLedger
from .models import Proposition


@dataclass
class CompiledArtifacts:
    evidence_graph: dict[str, Any]
    constraint_report: dict[str, Any]
    evidence_debt: list[dict[str, Any]]
    coverage_reports: list[dict[str, Any]] = field(default_factory=list)


def compile_v17_artifacts(
    propositions: list[Proposition],
    out_dir: Path,
    execution_ledger: ExecutionLedger | None = None,
    avenue_attempts: dict[str, list[dict[str, Any]]] | None = None,
    avenue_support: dict[str, list[dict[str, Any]]] | None = None,
) -> CompiledArtifacts:
    constraints = propagate_constraints(propositions)
    debt = calculate_evidence_debt(propositions)
    coverage_reports = run_all_coverage_gates(avenue_attempts or {}, avenue_support)
    artifacts = CompiledArtifacts(
        evidence_graph={"propositions": [p.to_dict() for p in propositions]},
        constraint_report={"constraints": [c.__dict__ for c in constraints]},
        evidence_debt=[item.__dict__ for item in debt],
        coverage_reports=[r.to_dict() for r in coverage_reports],
    )
    validation_errors = validate_v17_completion(artifacts, execution_ledger)
    coverage_errors = [e for r in coverage_reports for e in r.errors]
    if validation_errors:
        raise ValueError("; ".join(validation_errors))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evidence-graph.json").write_text(json.dumps(artifacts.evidence_graph, indent=2) + "\n")
    (out_dir / "constraint-report.json").write_text(json.dumps(artifacts.constraint_report, indent=2) + "\n")
    (out_dir / "evidence-debt.json").write_text(json.dumps(artifacts.evidence_debt, indent=2) + "\n")
    (out_dir / "coverage-report.json").write_text(
        json.dumps(artifacts.coverage_reports, indent=2) + "\n")
    return artifacts


def validate_v17_completion(
    artifacts: CompiledArtifacts,
    execution_ledger: ExecutionLedger | None = None,
) -> list[str]:
    errors = []
    for proposition in artifacts.evidence_graph.get("propositions", []):
        if proposition.get("state") == "search_exhausted" and "recovery" not in proposition:
            errors.append(f"{proposition['id']}: missing exhaustion proof")
        if proposition.get("state") == "search_exhausted":
            strategies = proposition.get("recovery", {}).get("recovery_strategies", [])
            if execution_ledger is None:
                errors.append(f"{proposition['id']}: missing execution ledger")
            elif any(
                not strategy.get("execution_id")
                or not execution_ledger.is_executed(strategy["execution_id"])
                for strategy in strategies
            ):
                errors.append(f"{proposition['id']}: unverified recovery execution")
        if proposition.get("state") == "established" and not proposition.get("evidence_sufficiency_passed", False):
            errors.append(f"{proposition['id']}: evidence sufficiency gate not passed")
    return errors
