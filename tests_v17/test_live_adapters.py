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


def test_epo_ops_records_created_from_authenticated_data_without_refetch(tmp_path, monkeypatch):
    """EPO OPS artifacts must be recorded straight into the ledger.

    retrieve_citations() already fetched the data over an authenticated
    client; re-downloading through the generic fetcher fails with 403 and,
    before credentials existed, silently skipped evidence decisions.
    """
    from types import SimpleNamespace

    import engine_v17.live_adapters as la

    bundle = SimpleNamespace(
        patcit=[SimpleNamespace(xp_number=None)],
        nplcit=[],
        to_dict=lambda: {
            "patcit": [{"publication_number": "US5109844"}],
            "nplcit": [],
        },
    )

    class StubClient:
        def __init__(self):
            self.auth = SimpleNamespace(is_authenticated=True)

        def _url(self, path, params=None):
            return f"https://ops.epo.org/3.2/rest-services{path}"

    payloads = {
        "patents.google.com/patent/": (
            b'<tr itemprop="backwardReferences"><td itemprop="publicationNumber">US1</td></tr>'
        ),
        "api.crossref.org": json.dumps({"message": {"items": []}}).encode(),
        "api.worldbank.org": b"[{}]",
    }

    fetch_calls = []

    def fetch(url):
        fetch_calls.append(url)
        for marker, body in payloads.items():
            if marker in url:
                return body
        return b"<html></html>"

    monkeypatch.setattr(la, "_EPO_OPS_AVAILABLE", True)
    monkeypatch.setattr(la, "EpoOpsClient", StubClient)
    monkeypatch.setattr(la, "retrieve_citations", lambda pid, client, use_cache=True: bundle)

    ledger = ExecutionLedger("RUN-EPO")
    artifacts = run_live_phase_adapters(
        patent_id="US8527057B2",
        output_dir=tmp_path,
        ledger=ledger,
        fetcher=fetch,
    )

    action_types = [e.action_type for e in ledger.executions]
    assert "epo_ops_citation_retrieval" in action_types
    epo_record = next(e for e in ledger.executions if e.action_type == "epo_ops_citation_retrieval")
    assert epo_record.result_count == 1
    assert (tmp_path / "epo-ops-citations-us8527057b2.json").exists()

    # The authenticated data must be reused — no unauthenticated re-download.
    assert not any("ops.epo.org" in url for url in fetch_calls)

    decisions = json.loads((tmp_path / "adapter-evidence-decisions.json").read_text())
    decision_ids = {d["proposition_id"] for d in decisions}
    assert {"P-03-002", "P-04-002"} <= decision_ids

    parsed = json.loads((tmp_path / "parsed-domain-evidence.json").read_text())
    assert parsed["epo_ops_citations"]["patcit"]
    assert set(artifacts) >= {"evidence", "parsed"}
