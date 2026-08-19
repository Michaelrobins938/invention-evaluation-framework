import json

from engine_v17.execution import ExecutionLedger
from engine_v17.live_adapters import (
    HttpLiveAdapter,
    run_live_phase_adapters,
)


def test_http_adapter_records_request_and_raw_artifact(tmp_path):
    calls = []

    def fetch(url):
        calls.append(url)
        return b"<html>result</html>"

    ledger = ExecutionLedger("RUN-TEST")
    adapter = HttpLiveAdapter(fetcher=fetch)
    result = adapter.fetch(
        ledger,
        phase_id="03",
        action_type="patent_search",
        source="test-source",
        url="https://example.test/search?q=exoskeleton",
        query="exoskeleton",
        artifact_path=tmp_path / "raw.html",
        result_count=1,
    )
    assert calls == ["https://example.test/search?q=exoskeleton"]
    assert result.execution_id == "EX-03-00001"
    assert result.result_artifact == str(tmp_path / "raw.html")
    assert (tmp_path / "raw.html").read_bytes() == b"<html>result</html>"
    assert ledger.is_executed(result.execution_id)


def test_live_phase_runner_generates_phase_artifacts(tmp_path):
    payloads = {
        "patent": b'<tr itemprop="backwardReferences"><td itemprop="publicationNumber">US1</td></tr><tr itemprop="backwardReferences"><td itemprop="publicationNumber">US2</td></tr><tr itemprop="backwardReferences"><td itemprop="publicationNumber">US3</td></tr>',
        "literature": json.dumps({"message": {"items": [{"title": ["Exoskeleton control"]}]}}).encode(),
        "market": b'[{"page":1},{"value": [{"date":"2024","value":"100"}]}]',
        "partner": b'<html><title>partner result</title></html>',
    }

    def fetch(url):
        for key, body in payloads.items():
            if key in url:
                return body
        return b"{}"

    ledger = ExecutionLedger("RUN-TEST")
    artifacts = run_live_phase_adapters(
        patent_id="US1234567",
        output_dir=tmp_path,
        ledger=ledger,
        fetcher=fetch,
    )
    assert set(artifacts) == {"patent", "literature", "market", "partners", "recovery", "evidence", "parsed", "claim_mapping"}
    assert all(path.exists() for path in artifacts.values())
    assert len(ledger.executions) == 13
    assert all(record.result_artifact for record in ledger.executions)


def test_recovery_record_contains_diagnosis_troubleshooting_and_reassessment(tmp_path):
    ledger = ExecutionLedger("RUN-TEST")
    run_live_phase_adapters(
        patent_id="US1234567",
        output_dir=tmp_path,
        ledger=ledger,
        fetcher=lambda url: b"{}",
    )
    recovery = json.loads((tmp_path / "recovery-records.json").read_text())
    assert recovery["initial_failure"]["type"] == "insufficient_proposition_support"
    assert recovery["diagnosis"]["hypothesis"]
    assert recovery["troubleshooting"]["executed"] is True
    assert recovery["troubleshooting"]["execution_id"]
    assert len(recovery["strategies"]) == 5
    assert all(strategy["execution_id"] for strategy in recovery["strategies"])
    assert recovery["reassessment"]["state"] == "WORK QUEUE"
