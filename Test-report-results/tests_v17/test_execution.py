import json

import pytest
from pathlib import Path

from engine_v17.execution import (
    ArtifactProvenanceStatus,
    AvenueExecutionStatus,
    ExecutionLedger,
    PhaseStatus,
    RunStatus,
    create_run_manifest,
    validate_delivery,
)
from engine_v17.orchestrator import run_generic


PHASE_SKILLS = sorted(Path(__file__).parents[2].glob("skills/skill-*/SKILL.md"))


def test_execution_record_proves_an_action_was_run():
    ledger = ExecutionLedger(run_id="RUN-3470828")
    record = ledger.record(
        phase_id="05",
        action_type="patent_search",
        source="Google Patents",
        query="B61B13/08 superconducting shorted loops",
        result_count=12,
    )
    assert record.execution_id == "EX-05-00001"
    assert record.status == AvenueExecutionStatus.COMPLETE
    assert ledger.is_executed(record.execution_id)


def test_planned_action_is_not_execution():
    ledger = ExecutionLedger(run_id="RUN-3470828")
    record = ledger.plan(
        phase_id="05",
        action_type="patent_search",
        source="Espacenet",
        query="classification traversal",
    )
    assert record.status == AvenueExecutionStatus.NOT_STARTED
    assert not ledger.is_executed(record.execution_id)


def test_artifact_ingestion_is_distinct_from_phase_execution():
    ledger = ExecutionLedger(run_id="RUN-3470828")
    artifact = ledger.ingest_artifact("05", "/tmp/novelty.md")
    assert artifact.status == ArtifactProvenanceStatus.INGESTED
    assert artifact.phase_execution_status == "NOT_VERIFIED"
    assert not ledger.is_phase_executed("05")


def test_run_manifest_has_canonical_evaluation_directory(tmp_path):
    manifest = create_run_manifest("US3470828", tmp_path)
    assert manifest["invention_id"] == "US3470828"
    assert manifest["evaluation_dir"] == str(tmp_path)
    assert manifest["run_status"] == RunStatus.RUNNING.value


def test_delivery_requires_execution_ledger_and_rendered_outputs(tmp_path):
    manifest = create_run_manifest("US3470828", tmp_path)
    (tmp_path / "report.md").write_text("report")
    with pytest.raises(ValueError, match="execution-ledger"):
        validate_delivery(manifest, tmp_path)

    (tmp_path / "execution-ledger.json").write_text(json.dumps({"executions": []}))
    (tmp_path / "report.html").write_text("html")
    (tmp_path / "report.pdf").write_bytes(b"pdf")
    manifest["phase_status"] = {"compile": PhaseStatus.COMPLETED.value, "render": PhaseStatus.COMPLETED.value}
    result = validate_delivery(manifest, tmp_path)
    assert result["passed"] is True


def test_generic_orchestrator_uses_patent_identifier_and_run_contract(tmp_path):
    source = tmp_path / "input"
    output = tmp_path / "output"
    source.mkdir()
    (source / "submission-us1234567.md").write_text("# Electromagnetic suspension vehicle\n")
    (source / "avenue-ledger-us1234567-v17.md").write_text("# Ledger\n")
    run_generic("US1234567", source, output, fetcher=lambda url: b"{}")
    assert (output / "run-manifest.json").exists()
    assert (output / "execution-ledger.json").exists()
    assert (output / "report-us1234567-v17.md").exists()
    assert json.loads((output / "run-manifest.json").read_text())["invention_id"] == "US1234567"


def test_generic_orchestrator_preserves_original_pdf_provenance(tmp_path):
    source = tmp_path / "input"
    output = tmp_path / "output"
    (source / "source").mkdir(parents=True)
    (source / "source" / "US1234567.pdf").write_bytes(b"pdf")
    (source / "submission-us1234567.md").write_text("# Submission\n")
    run_generic("US1234567B2", source, output, fetcher=lambda url: b"{}")
    provenance = json.loads((output / "source-provenance.json").read_text())
    assert provenance["status"] == "ORIGINAL_ARTIFACT"


def test_source_only_clean_run_generates_submission_and_delivery(tmp_path):
    source = tmp_path / "input"
    output = tmp_path / "output"
    (source / "source").mkdir(parents=True)
    (source / "source" / "US1234567B2.html").write_text("<html>patent source</html>")
    run_generic("US1234567B2", source, output, fetcher=lambda url: b"{}")
    assert (output / "submission-us1234567b2.md").exists()
    assert (output / "run-manifest.json").exists()


def test_every_phase_skill_declares_the_v17_execution_contract():
    # skill-00-run-evaluation is the one-command runner entry point, not a
    # pipeline phase; the ten-phase contract check applies to phases 01–10.
    phase_skills = [p for p in PHASE_SKILLS if p.parent.name != "skill-00-run-evaluation"]
    assert len(phase_skills) == 10
    required_markers = (
        "run_id",
        "evaluation_dir",
        "execution ledger",
        "phase status",
        "Evidence Sufficiency Gate",
        "Failure Recovery Contract",
        "artifact",
    )
    for skill_path in phase_skills:
        text = skill_path.read_text(encoding="utf-8").lower()
        missing = [marker for marker in required_markers if marker.lower() not in text]
        assert not missing, f"{skill_path}: missing contract markers {missing}"
