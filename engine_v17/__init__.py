"""Evidence-constrained inference controls for Invention Evaluation Engine v1.7 + Autoprompt integration."""

from .models import (
    EvidenceLeverage,
    EvidenceState,
    Proposition,
    ResolutionState,
    ResearchExhaustion,
    UnknownType,
)
from .execution import (
    ArtifactProvenanceStatus,
    AvenueExecutionStatus,
    ExecutionLedger,
    PhaseStatus,
    RunStatus,
)

# Autoprompt integration layer (IEF Execution Contract v1.0.0)
try:
    from .mission import EvaluationMission, create_mission  # noqa: F401
    from .dag import build_dag, launch_groups, dag_to_execution_plan  # noqa: F401
    from .status import CombinedStatus, ExecutionStatus, EvidenceStatus  # noqa: F401
    from .epistemic_gates import run_all_gates, GateVerdict  # noqa: F401
    from .review import ReviewRecord, ArbitrationRecord  # noqa: F401
    from .autoprompt_adapter import (  # noqa: F401
        adapt_autoprompt_mission_to_ief,
        build_execution_plan,
        create_unified_run_manifest,
    )
except ImportError:
    pass

__all__ = [
    "EvidenceLeverage",
    "EvidenceState",
    "Proposition",
    "ResolutionState",
    "ResearchExhaustion",
    "UnknownType",
    "AvenueExecutionStatus",
    "ArtifactProvenanceStatus",
    "ExecutionLedger",
    "PhaseStatus",
    "RunStatus",
]
