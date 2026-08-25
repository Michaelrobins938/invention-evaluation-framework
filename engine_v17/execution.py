"""Canonical execution and delivery records for v1.7 runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any


class RunStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_EVIDENCE_DEBT = "COMPLETED_WITH_EVIDENCE_DEBT"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class PhaseStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_EVIDENCE_DEBT = "COMPLETED_WITH_EVIDENCE_DEBT"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class AvenueExecutionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    REQUIRES_VERIFICATION = "REQUIRES_VERIFICATION"


class ArtifactProvenanceStatus(str, Enum):
    INGESTED = "INGESTED"
    GENERATED = "GENERATED"


@dataclass
class ArtifactRecord:
    phase_id: str
    path: str
    status: ArtifactProvenanceStatus
    phase_execution_status: str = "NOT_VERIFIED"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status.value
        return result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_invention_id(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "", value).upper()
    if not normalized:
        raise ValueError("invention_id must contain letters or numbers")
    return normalized


@dataclass
class ExecutionRecord:
    execution_id: str
    run_id: str
    phase_id: str
    action_type: str
    source: str
    query: str
    request: str = ""
    started_at: str = ""
    completed_at: str = ""
    result_count: int | None = None
    result_artifact: str | None = None
    status: AvenueExecutionStatus = AvenueExecutionStatus.IN_PROGRESS
    outcome: str = ""
    candidate_evidence: bool = False
    evidence_sufficiency: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass
class ExecutionLedger:
    run_id: str
    executions: list[ExecutionRecord] = field(default_factory=list)
    artifacts: list[ArtifactRecord] = field(default_factory=list)

    def _next_id(self, phase_id: str) -> str:
        count = sum(record.phase_id == phase_id for record in self.executions) + 1
        return f"EX-{phase_id}-{count:05d}"

    def plan(self, phase_id: str, action_type: str, source: str, query: str, request: str = "") -> ExecutionRecord:
        record = ExecutionRecord(
            execution_id=self._next_id(phase_id),
            run_id=self.run_id,
            phase_id=phase_id,
            action_type=action_type,
            source=source,
            query=query,
            request=request,
            started_at="",
            status=AvenueExecutionStatus.NOT_STARTED,
        )
        self.executions.append(record)
        return record

    def record(
        self,
        phase_id: str,
        action_type: str,
        source: str,
        query: str,
        result_count: int | None = None,
        request: str = "",
        result_artifact: str | None = None,
        outcome: str = "",
        candidate_evidence: bool = False,
        evidence_sufficiency: bool = False,
        status: AvenueExecutionStatus | None = None,
    ) -> ExecutionRecord:
        now = _now()
        record = ExecutionRecord(
            execution_id=self._next_id(phase_id),
            run_id=self.run_id,
            phase_id=phase_id,
            action_type=action_type,
            source=source,
            query=query,
            request=request,
            started_at=now,
            completed_at=now,
            result_count=result_count,
            result_artifact=result_artifact,
            status=status if status is not None else AvenueExecutionStatus.COMPLETE,
            outcome=outcome,
            candidate_evidence=candidate_evidence,
            evidence_sufficiency=evidence_sufficiency,
        )
        self.executions.append(record)
        return record

    def is_executed(self, execution_id: str) -> bool:
        return any(
            record.execution_id == execution_id
            and record.status in {AvenueExecutionStatus.COMPLETE, AvenueExecutionStatus.BLOCKED}
            and bool(record.started_at)
            and bool(record.completed_at)
            for record in self.executions
        )

    def ingest_artifact(
        self,
        phase_id: str,
        path: str,
        phase_execution_status: str = "NOT_VERIFIED",
    ) -> ArtifactRecord:
        artifact = ArtifactRecord(
            phase_id,
            path,
            ArtifactProvenanceStatus.INGESTED,
            phase_execution_status,
        )
        self.artifacts.append(artifact)
        return artifact

    def is_phase_executed(self, phase_id: str) -> bool:
        return any(
            record.phase_id == phase_id
            and record.status == AvenueExecutionStatus.COMPLETE
            and record.action_type != "phase_artifact_ingestion"
            for record in self.executions
        )

    def attempts_by_phase(self, phase_id: str) -> list[dict[str, Any]]:
        """Return the recorded execution attempts for a phase as plain dicts.

        The coverage gates consume these to check that required sources,
        minimum attempt counts, and required fields were actually gathered —
        so a substitution (Crossref for a domain source, a NAICS code for a
        bounded market model, a candidate list for a partner-fit analysis)
        is machine-detectable rather than resting on reviewer judgment.
        """
        out: list[dict[str, Any]] = []
        for record in self.executions:
            if record.phase_id != phase_id:
                continue
            if record.action_type == "phase_artifact_ingestion":
                continue
            out.append({
                "source": record.source,
                "method": record.action_type,
                "query": record.query,
                "result_count": record.result_count,
                "outcome": record.outcome,
                "execution_id": record.execution_id,
            })
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "executions": [record.to_dict() for record in self.executions],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }

    def write(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "execution-ledger.json"
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        return path


def create_run_manifest(invention_id: str, evaluation_dir: Path, pipeline_version: str = "v1.7") -> dict[str, Any]:
    normalized = normalize_invention_id(invention_id)
    return {
        "run_id": f"RUN-{normalized}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "invention_id": normalized,
        "pipeline_version": pipeline_version,
        "evaluation_dir": str(evaluation_dir),
        "run_status": RunStatus.RUNNING.value,
        "phase_status": {},
        "created_at": _now(),
    }


def validate_delivery(manifest: dict[str, Any], evaluation_dir: Path) -> dict[str, Any]:
    required = [
        "execution-ledger.json",
        "report.md",
        "report.html",
        "report.pdf",
    ]
    missing = [name for name in required if not (evaluation_dir / name).is_file() or (evaluation_dir / name).stat().st_size == 0]
    if missing:
        raise ValueError(f"missing delivery artifacts: {', '.join(missing)}")
    phase_status = manifest.get("phase_status", {})
    if phase_status.get("compile") not in {PhaseStatus.COMPLETED.value, PhaseStatus.COMPLETED_WITH_EVIDENCE_DEBT.value}:
        raise ValueError("compile phase is not complete")
    if phase_status.get("render") != PhaseStatus.COMPLETED.value:
        raise ValueError("render phase is not complete")
    return {"passed": True, "evaluation_dir": str(evaluation_dir), "artifacts": required}
