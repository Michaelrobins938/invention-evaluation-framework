from engine_v17.claim_graph import decompose_claim, derive_claim_vectors
from engine_v17.rights_graph import build_rights_graph, legal_leverage
from engine_v17.models import Proposition
from engine_v17.recovery import RecoveryAttempt, transition_state
import json
from pathlib import Path
import pytest
from engine_v17.orchestrator import run


def _evaluation_root():
    candidates = [Path(__file__).parents[2], Path.cwd()]
    for candidate in candidates:
        if (candidate / "evaluations" / "us8527057").exists():
            return candidate
    return None


def test_us8527057_v17_acceptance_core_constraints():
    rights = build_rights_graph([{
        "patent": "US8527057B2",
        "status": {"active": False, "state": "EXPIRED"},
    }])
    assert legal_leverage(rights).state == "minimal"
    claim = decompose_claim({
        "id": "US8527057-claim-1",
        "text": "retinal electrode array, scleral strap, hermetic flip-chip package, cable, coplanar inductive coil",
    })
    assert {v.kind for v in derive_claim_vectors(claim)} == {"product", "process", "dependent"}
    proposition = Proposition(id="P-05-001", claim="Claim 1 anticipation")
    assert transition_state(proposition, []) .value == "escalation_required"


def test_compiled_us8527057_artifacts_propagate_status_and_debt():
    base = _evaluation_root()
    if base is None:
        pytest.skip("project evaluation fixtures are not installed with the global skill")
    root = base / "evaluations" / "us8527057-v17"
    rights = json.loads((root / "rights-graph.json").read_text())
    debt = json.loads((root / "evidence-debt.json").read_text())
    bridge = json.loads((root / "bridge-vector.json").read_text())
    assert rights["status"]["state"] == "EXPIRED"
    assert rights["status"]["active"] is False
    assert bridge["state"] == "partially_traversed"
    assert any(item["proposition_id"] == "P-05-001" for item in debt)


def test_orchestrator_writes_v17_report_and_artifacts(tmp_path):
    base = _evaluation_root()
    if base is None:
        pytest.skip("project evaluation fixtures are not installed with the global skill")
    source = base / "evaluations" / "us8527057"
    output = tmp_path / "us8527057-v17"
    run(source, output)
    assert (output / "report-us8527057-v17.md").exists()
    assert json.loads((output / "rights-graph.json").read_text())["status"]["state"] == "EXPIRED"
    assert "UNRESOLVED — SEARCH-INCOMPLETE" in (output / "report-us8527057-v17.md").read_text()
    source = json.loads((output / "patent-source-us8527057.json").read_text())
    assert source["counts"]["forward_references"] >= 1
    assert source["counts"]["backward_references"] >= 1


def test_us8527057_query_and_family_regressions_are_exposed():
    base = _evaluation_root()
    if base is None:
        pytest.skip("project evaluation fixtures are not installed with the global skill")
    source = base / "evaluations" / "us8527057"
    report = (source / "report-us8527057-e2e-v16.md").read_text()
    scores = json.loads((source / "scores-us8527057.json").read_text())
    status = json.loads((source / "status-record-us8527057.json").read_text())
    assert "A61N1/0543 AND retinal" in report
    assert "A61N 1/18 AND (retinal OR epiretinal OR ocular implant)" not in report
    assert "25–26 YTD" in scores["charts"]["activity_line"]["data"]
    members = {m["patent"]: m["state"] for m in status["family"]["members"]}
    assert members["US7881799B2"] == "ACTIVE"
    assert members["US8473048B2"] == "ACTIVE"
