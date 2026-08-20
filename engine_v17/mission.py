"""First-class Evaluation Mission artifact.

Autoprompt receives the mission and turns it into an execution plan.
IEF determines the domain-specific requirements of that mission.
Workers may not redefine the global mission.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .execution import normalize_invention_id


@dataclass(frozen=True)
class EvidencePolicy:
    schema_ref: str = "schemas/evidence-contract.schema.json"
    corroboration_required: bool = True
    minimum_independent_sources: int = 2
    temporal_policy: str = "pre_filing"  # pre_filing | in_period | any


@dataclass(frozen=True)
class OutputContract:
    evaluation_dir: str
    required_artifacts: tuple[str, ...] = (
        "report.md",
        "report.html",
        "report.pdf",
        "run-manifest.json",
        "execution-ledger.json",
        "evidence-graph.json",
        "proposition-ledger.json",
    )


@dataclass
class EvaluationMission:
    """Immutable evaluation mission. Workers must not mutate it."""

    evaluation_id: str
    target: str
    target_type: str  # patent | publication | submission | mixed
    mission: str
    scope: str  # full-pipeline | landscape-only | novelty-only | market-only | custom
    framework_version: str
    execution_version: str
    evidence_policy: EvidencePolicy
    required_domains: list[str]
    output_contract: OutputContract
    success_criteria: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    temporal_scope: dict[str, Any] = field(default_factory=dict)
    required_verification: dict[str, bool] = field(default_factory=lambda: {
        "independent_review": True, "fresh_verification": True, "arbitration": True
    })
    escalation_rules: dict[str, Any] = field(default_factory=dict)
    execution_budget: dict[str, Any] = field(default_factory=dict)
    run_id: str = ""

    def __post_init__(self) -> None:
        # Normalize evaluation_id
        object.__setattr__(self, "evaluation_id", normalize_invention_id(self.evaluation_id))
        if not self.run_id:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            object.__setattr__(self, "run_id", f"RUN-{self.evaluation_id}-{ts}")

    @property
    def mission_hash(self) -> str:
        return hashlib.sha256(self.mission.encode("utf-8")).hexdigest()

    @property
    def mission_bytes(self) -> int:
        return len(self.mission.encode("utf-8"))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Convert nested dataclasses
        d["evidence_policy"] = asdict(self.evidence_policy) if isinstance(self.evidence_policy, EvidencePolicy) else self.evidence_policy
        oc = asdict(self.output_contract) if isinstance(self.output_contract, OutputContract) else dict(self.output_contract)
        # JSON schema expects array (list), not tuple
        if "required_artifacts" in oc and isinstance(oc["required_artifacts"], tuple):
            oc["required_artifacts"] = list(oc["required_artifacts"])
        d["output_contract"] = oc
        d["mission_hash"] = self.mission_hash
        d["mission_bytes"] = self.mission_bytes
        return d

    def write(self, evaluation_dir: Path) -> Path:
        evaluation_dir.mkdir(parents=True, exist_ok=True)
        path = evaluation_dir / "evaluation-mission.json"
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        return path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationMission":
        ep = data.get("evidence_policy", {})
        if isinstance(ep, dict):
            ep_obj = EvidencePolicy(**{k: v for k, v in ep.items() if k in EvidencePolicy.__dataclass_fields__})
        else:
            ep_obj = ep
        oc = data.get("output_contract", {})
        if isinstance(oc, dict):
            # evaluation_dir is required
            required = tuple(oc.get("required_artifacts", OutputContract.required_artifacts))
            oc_obj = OutputContract(evaluation_dir=oc["evaluation_dir"], required_artifacts=required)
        else:
            oc_obj = oc
        return cls(
            evaluation_id=data["evaluation_id"],
            target=data["target"],
            target_type=data.get("target_type", "patent"),
            mission=data["mission"],
            scope=data.get("scope", "full-pipeline"),
            framework_version=data.get("framework_version", "v1.7"),
            execution_version=data.get("execution_version", "autoprompt-1.0.3-opencode"),
            evidence_policy=ep_obj,
            required_domains=list(data.get("required_domains", [])),
            output_contract=oc_obj,
            success_criteria=list(data.get("success_criteria", [])),
            dependencies=list(data.get("dependencies", [])),
            constraints=dict(data.get("constraints", {})),
            temporal_scope=dict(data.get("temporal_scope", {})),
            required_verification=dict(data.get("required_verification", {"independent_review": True, "fresh_verification": True, "arbitration": True})),
            escalation_rules=dict(data.get("escalation_rules", {})),
            execution_budget=dict(data.get("execution_budget", {})),
            run_id=data.get("run_id", ""),
        )

    @classmethod
    def load(cls, path: Path) -> "EvaluationMission":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.evaluation_id:
            errors.append("evaluation_id required")
        if not self.mission or len(self.mission) < 10:
            errors.append("mission required (min 10 chars)")
        if self.target_type not in ("patent", "publication", "submission", "mixed"):
            errors.append(f"invalid target_type: {self.target_type}")
        if self.scope not in ("full-pipeline", "landscape-only", "novelty-only", "market-only", "custom"):
            errors.append(f"invalid scope: {self.scope}")
        if not self.required_domains:
            errors.append("required_domains must not be empty")
        if not self.output_contract.evaluation_dir:
            errors.append("output_contract.evaluation_dir required")
        return errors


def create_mission(
    evaluation_id: str,
    target: str,
    mission_text: str | None = None,
    scope: str = "full-pipeline",
    evaluation_dir: str | Path | None = None,
    framework_version: str = "v1.7",
    execution_version: str = "autoprompt-1.0.3-opencode",
    required_domains: list[str] | None = None,
    **kwargs: Any,
) -> EvaluationMission:
    """Factory with sensible defaults for the 10-phase pipeline."""
    if required_domains is None:
        if scope == "full-pipeline":
            required_domains = [
                "gather-submission", "analyze-technology", "patent-landscape",
                "novelty-search", "literature-search", "market-opportunity",
                "identify-partners", "compile-report", "render-report",
            ]
        elif scope == "landscape-only":
            required_domains = ["gather-submission", "analyze-technology", "patent-landscape"]
        elif scope == "novelty-only":
            required_domains = ["gather-submission", "analyze-technology", "novelty-search"]
        elif scope == "market-only":
            required_domains = ["gather-submission", "analyze-technology", "market-opportunity"]
        else:
            required_domains = ["gather-submission", "analyze-technology"]

    if mission_text is None:
        mission_text = f"Evaluate invention {normalize_invention_id(evaluation_id)} end-to-end through the IEF evidence-constrained pipeline"

    if evaluation_dir is None:
        evaluation_dir = f"evaluations/{normalize_invention_id(evaluation_id).lower()}"

    return EvaluationMission(
        evaluation_id=evaluation_id,
        target=target,
        target_type=kwargs.pop("target_type", "patent"),
        mission=mission_text,
        scope=scope,
        framework_version=framework_version,
        execution_version=execution_version,
        evidence_policy=kwargs.pop("evidence_policy", EvidencePolicy()),
        required_domains=required_domains,
        output_contract=OutputContract(evaluation_dir=str(evaluation_dir)),
        success_criteria=kwargs.pop("success_criteria", [
            {"criterion": "execution_completion", "threshold": "COMPLETED or COMPLETED_WITH_EVIDENCE_DEBT"},
            {"criterion": "evidence_coverage", "threshold": "all coverage gates dispositioned"},
            {"criterion": "overclaim_rate", "threshold": "0 - no unsupported inference promoted"},
        ]),
        **kwargs,
    )
