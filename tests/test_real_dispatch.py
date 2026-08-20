"""Phase 2: Real Autoprompt dispatch + evidence flow + review + hermetic.

Proves:
- REAL_AUTOPROMPT lane dispatch (no LEGACY_FALLBACK)
- DAG launch groups executed
- Structured outputs enter evidence machinery
- E0-E9 consume real evidence (E0-E2 PASS, E3 FAILED is correct for insufficient, not placeholder)
- E7/E8 real execution with review-ledger persistence
- Arbitration path available
- Scores satisfy provenance (target_patent)
- Hermetic live adapters: SourceObject → evidence gate → ledger
- A/B/C execution provenance distinct
- No legacy fallback in integrated mode
- Multi-run consistency (3 runs)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


def test_real_autoprompt_lane_dispatch():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True, execution_mode="REAL_AUTOPROMPT")
        assert r["execution_mode"] == "REAL_AUTOPROMPT"
        assert r["manifest"]["all_lanes_real"] is True
        assert r["manifest"]["execution_provenance"] == "autoprompt"
        assert "REAL_AUTOPROMPT" in str(r["manifest"])
        # Every lane must be REAL
        for lane in r["lane_dispatch_log"]:
            assert lane["execution_mode"] == "REAL_AUTOPROMPT"
            assert lane["persona"].startswith("ap-")
        # No legacy fallback
        assert not any("LEGACY" in str(v) for v in r["manifest"].values() if isinstance(v, str))


def test_dag_launch_groups_parallel():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True)
        groups = r["plan"]["launch_groups"]
        # Group 2 should have 3 parallel nodes (patent, literature, market)
        assert any(len(g) == 3 for g in groups)
        # Topological order respects dependencies
        order = r["plan"]["topological_order"]
        assert order.index("gather-submission") < order.index("analyze-technology")
        assert order.index("analyze-technology") < order.index("compile-report")


def test_evidence_flow_real_e0_e9():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True)
        gates = {g["gate"]: g for g in r["gates"]}
        # Real evidence: E0 intake PASS (submission present), E1 source PASS, E2 proposition PASS
        assert gates["E0"]["verdict"] == "PASSED", gates["E0"]
        assert gates["E1"]["verdict"] == "PASSED", gates["E1"]
        assert gates["E2"]["verdict"] == "PASSED", gates["E2"]
        # E3 should be FAILED for this fixture (insufficient evidence is correct, not placeholder empty)
        assert gates["E3"]["verdict"] == "FAILED"
        assert gates["E3"]["barrier_type"] == "insufficient_corroboration"
        # Combined status reflects real evidence
        assert r["combined_status"]["execution"] in ("COMPLETED_WITH_EVIDENCE_DEBT", "COMPLETE")
        assert r["combined_status"]["evidence"] == "INSUFFICIENT"


def test_scores_provenance_target_patent():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True)
        scores = json.loads((out / "scores-manifest.json").read_text())
        assert "target_patent" in scores
        assert scores["target_patent"]["publication_number"] == "US8527057B2"
        assert "evidence_items" in scores
        assert len(scores["evidence_items"]) > 0


def test_review_fresh_verification_real_gates():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True)
        review_path = out / "review-ledger.json"
        assert review_path.exists()
        ledger = json.loads(review_path.read_text())
        assert len(ledger["reviews"]) >= 6  # 3 propositions × reviewer+verifier
        # Check independence and blind flags
        for rev in ledger["reviews"]:
            assert rev["is_independent"] is True
        # Fresh verifiers are blind
        verifiers = [x for x in ledger["reviews"] if x["is_blind"]]
        assert len(verifiers) >= 3
        # E7/E8 gates should be PASSED based on real reviews
        gates = {g["gate"]: g for g in r["gates"]}
        assert gates["E7"]["verdict"] == "PASSED", gates["E7"]
        assert gates["E8"]["verdict"] == "PASSED", gates["E8"]


def test_arbitration_available_on_disagreement():
    from engine_v17.review import independent_review, fresh_verification, arbitrate, ReviewVerdict
    rev = independent_review("P-TEST-001", ["src"], "ap-implementer", "ap-reviewer", verdict=ReviewVerdict.PASSED)
    ver = fresh_verification("P-TEST-001", ["src"], "ap-implementer", "ap-fresh-verifier", verdict=ReviewVerdict.FAILED)
    arb = arbitrate("P-TEST-001", rev, ver, verdict=ReviewVerdict.FAILED, basis="arbiter sides with verifier")
    assert arb.verdict == ReviewVerdict.FAILED
    assert arb.arbiter == "ap-arbiter"


def test_hermetic_live_adapter_chain():
    """Hermetic live adapters preserve source distinctions and feed evidence gate → ledger."""
    from pathlib import Path as P
    import tempfile
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        eval_dir = P(tmp) / "eval"
        eval_dir.mkdir()
        (eval_dir / "submission-US9999999.md").write_text("# Submission\n\nDisclosure: none\n")
        out = P(tmp) / "out"
        r = run_with_autoprompt("US9999999", str(eval_dir / "submission-US9999999.md"), out, eval_dir, hermetic=True)
        assert r["execution_mode"] == "REAL_AUTOPROMPT"
        # Parsed domains must exist with distinct payloads
        parsed = json.loads((out / "parsed-domain-evidence.json").read_text())
        assert "patent" in parsed
        assert "literature" in parsed
        assert isinstance(parsed["literature"], list)
        assert len(parsed["literature"]) >= 1
        assert "DOI" in str(parsed["literature"][0]) or "doi" in str(parsed["literature"][0]).lower()
        # Evidence decisions must be WORK QUEUE (not fabricated)
        decisions = json.loads((out / "adapter-evidence-decisions.json").read_text())
        assert all(d["state"] == "WORK QUEUE" for d in decisions)


def test_ab_execution_provenance_distinct():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out_a = Path(tmp) / "a"
        out_b = Path(tmp) / "b"
        a = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out_a, Path("evaluations/us8527057"), execution_mode="LEGACY_FALLBACK")
        b = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out_b, Path("evaluations/us8527057"), execution_mode="REAL_AUTOPROMPT", hermetic=True)
        assert a["execution_mode"] == "LEGACY_FALLBACK"
        assert b["execution_mode"] == "REAL_AUTOPROMPT"
        assert a["manifest"]["execution_provenance"] == "legacy"
        assert b["manifest"]["execution_provenance"] == "autoprompt"
        # Lane dispatch log only in REAL
        assert "lane_dispatch_log" not in a["manifest"] or not a["manifest"].get("all_lanes_real")
        assert b["manifest"]["all_lanes_real"] is True


def test_no_legacy_fallback_in_integrated_mode():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True, execution_mode="REAL_AUTOPROMPT")
        manifest_text = json.dumps(r["manifest"])
        assert "LEGACY_FALLBACK" not in manifest_text
        assert r["manifest"]["execution_mode"] == "REAL_AUTOPROMPT"


def test_multi_run_consistency():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    results = []
    for i in range(3):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True)
            results.append(r["combined_status"]["evidence"])
    assert len(set(results)) == 1  # all INSUFFICIENT

def test_no_recursive_orchestration():
    from engine_v17.orchestrator_autoprompt import run_with_autoprompt
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        r = run_with_autoprompt("US8527057", "evaluations/us8527057/source/US8527057.pdf", out, Path("evaluations/us8527057"), hermetic=True)
        ledger = json.loads((out / "execution-ledger.json").read_text())
        # No execution should have phase_id 00 with autoprompt re-invocation
        for ex in ledger["executions"]:
            assert not (ex.get("phase_id") == "00" and "autoprompt" in ex.get("action_type", "").lower())
