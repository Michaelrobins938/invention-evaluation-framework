"""Anti-quit enforcement — the pipeline must attempt every acquisition route.

Proves:
  1. Queries derive from THIS invention's submission (no fixture subjects).
  2. Patent identity resolution follows a route ladder; each route is recorded.
  3. A source is BLOCKED only after every route was attempted.
  4. A research lane with zero retrieval attempts downgrades delivery status
     (lazy-quit detection).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine_v17.execution import AvenueExecutionStatus, ExecutionLedger
from engine_v17.live_adapters import derive_invention_terms, run_live_phase_adapters


# ---------------------------------------------------------------------------
# Query derivation — wrong-subject searches are prohibited
# ---------------------------------------------------------------------------

def test_terms_derived_from_this_invention_not_fixtures():
    text = (
        "# Submission\n\n## Invention Name\nAdaptive Energy Harvesting System\n\n"
        "A method for adaptive energy harvesting using thermoelectric transducers "
        "and piezoelectric transducers. The harvesting controller reallocates power. "
        "Harvesting efficiency is monitored."
    )
    terms = derive_invention_terms(text)
    assert "harvesting" in terms
    assert "exoskeleton" not in terms.lower()
    assert "locomotion" not in terms.lower()


def test_stopwords_and_legalese_excluded():
    terms = derive_invention_terms(
        "The invention disclosure claims a system method device wherein said apparatus "
        "comprises a capacitor capacitor capacitor"
    )
    assert "invention" not in terms.split()
    assert "wherein" not in terms.split()
    assert "capacitor" in terms


def test_empty_submission_falls_back_gracefully():
    assert derive_invention_terms("") == ""
    assert derive_invention_terms(None) == ""


# ---------------------------------------------------------------------------
# Route ladder — one failed fetch never terminates resolution
# ---------------------------------------------------------------------------

class _AlwaysFailsFetcher:
    def __call__(self, url: str) -> bytes:
        raise RuntimeError(f"HTTP 404 for {url}")


class _FailsUntilSearchFetcher:
    """404s direct/granted routes, serves a search page resolving to US9999999."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if "?q=" in url and "/patent/" not in url:
            return (b"<html><body>" + b"x" * 300 +
                    b'<a href="/patent/US9999999/en">hit</a></body></html>')
        if url.endswith("US9999999/en"):
            return b"<html><body>patent page content</body></html>"
        raise RuntimeError("HTTP 404")


def _run(tmp_path: Path, fetcher) -> tuple[ExecutionLedger, dict]:
    ledger = ExecutionLedger("test-run-escalation")
    out = tmp_path / "out"
    artifacts = run_live_phase_adapters(
        patent_id="8530", output_dir=out, ledger=ledger,
        fetcher=fetcher,
        submission_text="Adaptive energy harvesting controller with thermoelectric transducers",
    )
    return ledger, artifacts


def test_total_failure_attempts_every_route_then_blocks(tmp_path):
    ledger, artifacts = _run(tmp_path, _AlwaysFailsFetcher())
    patent_records = [r for r in ledger.executions if r.phase_id == "03" and r.action_type == "patent_search"]
    assert len(patent_records) >= 3, "every route must be attempted and individually recorded"
    final = patent_records[-1]
    assert final.status == AvenueExecutionStatus.BLOCKED
    assert "all" in final.outcome and "routes blocked" in final.outcome
    raw = Path(final.result_artifact).read_text(encoding="utf-8")
    assert "routes:" in raw


def test_resolution_succeeds_on_later_route_without_quitting(tmp_path):
    fetcher = _FailsUntilSearchFetcher()
    ledger, artifacts = _run(tmp_path, fetcher)
    patent_records = [r for r in ledger.executions if r.action_type == "patent_search"]
    statuses = [r.status for r in patent_records]
    assert statuses[0] == AvenueExecutionStatus.BLOCKED
    assert statuses[-1] == AvenueExecutionStatus.COMPLETE
    assert any("US9999999" in r.query for r in patent_records)


def test_failed_retrieval_artifacts_carry_debt_notes(tmp_path):
    ledger, artifacts = _run(tmp_path, _AlwaysFailsFetcher())
    out = Path(ledger.executions[0].result_artifact).parent
    raw = out / "raw-literature-crossref.json"
    content = raw.read_text(encoding="utf-8")
    assert "Retrieval blocked" in content
    assert "Crossref" in content
    # Phase artifacts report the avenue as BLOCKED, never as success
    lit_phase = next(out.glob("literature-search-*.md")).read_text(encoding="utf-8")
    assert "BLOCKED" in lit_phase
    assert "live response retrieved" not in lit_phase


def test_derived_queries_used_not_fixture_subjects(tmp_path):
    ledger, _ = _run(tmp_path, _AlwaysFailsFetcher())
    queries = " | ".join(r.query for r in ledger.executions)
    assert "exoskeleton" not in queries.lower()
    assert "rewalk" not in queries.lower()
    assert "harvesting" in queries.lower()


# ---------------------------------------------------------------------------
# Lazy-quit detection at delivery
# ---------------------------------------------------------------------------

def test_research_lane_gaps_detects_unattempted_channels():
    from engine_v17.orchestrator_autoprompt import research_lane_gaps
    ledger = ExecutionLedger("run-gaps")
    ledger.record("03", "patent_search", "Google Patents", "q", result_count=None)
    ledger.record("06", "market-opportunity", "local filesystem", "ingested market analysis")  # worker-style record counts
    gaps = research_lane_gaps(ledger)
    assert set(gaps.values()) == {"literature-search", "novelty-search", "identify-partners"}
    assert "patent-landscape" not in gaps.values()
    assert "market-opportunity" not in gaps.values()


def test_no_gaps_when_all_lanes_attempted():
    from engine_v17.orchestrator_autoprompt import research_lane_gaps
    ledger = ExecutionLedger("run-full")
    for phase in ("03", "04", "05", "06", "07"):
        rec = ledger.record(phase, f"lane-{phase}-work", "src", "q")
        rec.status = AvenueExecutionStatus.COMPLETE
    assert research_lane_gaps(ledger) == {}
