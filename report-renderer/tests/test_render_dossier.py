"""Hermetic tests for the 12-module Patent Intelligence Dossier renderer.

No BigQuery, LLM, or chromium required: the renderer is tested against a
minimal CIR package and the deterministic metric formulas.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import render_dossier as rd


MINIMAL_CIR = {
    "patent_number": "US-6506148-B2",
    "audit": {"sha256": "a" * 64, "schema_version": "cir-1.0", "bytes": 100},
    "claims": [
        {
            "patent_number": "US-6506148-B2",
            "claim_number": 1,
            "independent": True,
            "elements": [
                {
                    "element_id": "A",
                    "raw_text": "a monitor displaying an image",
                    "causal_mechanism": {
                        "input_state": "image",
                        "transformation": "pulse at 0.1-15 Hz",
                        "output_state": "pulsed field",
                    },
                    "dependencies": [],
                    "prior_art_collisions": [
                        {
                            "reference_id": "US-1-A",
                            "tier": "Tier 2: Combination Threat",
                            "overlapping_mechanisms": ["field delivery"],
                            "reasoning": "combination reading",
                            "confidence_score": 0.5,
                            "evidence": {
                                "source_type": "patent_claim",
                                "document_id": "US-1-A",
                                "location": "claim 1",
                                "hash_timestamp": "sha256:deadbeef@2026-01-01T00:00:00+00:00",
                            },
                        }
                    ],
                }
            ],
        }
    ],
}


@pytest.fixture
def cir_file(tmp_path):
    p = tmp_path / "cir.json"
    p.write_text(json.dumps(MINIMAL_CIR), encoding="utf-8")
    return p


def test_render_dossier_contains_all_12_modules(cir_file):
    html = rd.render_dossier(cir_file)
    for n in range(1, 13):
        assert f"Module {n}" in html, f"Module {n} missing"


def test_empty_data_rule_renders_established_note(cir_file):
    # No status file: family timeline / FTO / weapon map must render
    # established-notes instead of being omitted.
    html = rd.render_dossier(cir_file)
    assert "No family timeline identified in the current boundary" in html
    assert "No prosecution-history estoppel identified in the current boundary" in html
    assert "no blocking patents identified in the current boundary" in html
    assert "no commercial products identified in the current boundary" in html


def test_module2_binds_audit_hash(cir_file):
    html = rd.render_dossier(cir_file)
    assert ("a" * 12 + "…") in html


def test_module5_renders_kill_chain_with_vulnerability(cir_file):
    html = rd.render_dossier(cir_file)
    assert "Tier 2: Combination Threat" in html
    # vulnerability = 0.8 (tier weight) * 0.5 (confidence) = 40
    assert "40 (" in html


def test_module12_verdict_and_falsifiability(cir_file):
    html = rd.render_dossier(cir_file)
    assert "VERDICT:" in html
    assert "What would change this conclusion" in html
    assert "0-30 days" in html and "90-180 days" in html


def test_derive_metrics_deterministic_formulas():
    metrics = rd.derive_metrics(MINIMAL_CIR, None)
    gauges = {g["label"]: g["score"] for g in metrics["gauges"]}
    # Claim strength formula: 62
    assert gauges["Claim Strength"] == 62
    # Prior-art vulnerability: max tier_weight*confidence = 0.8*0.5 = 40
    assert gauges["Prior-Art Vulnerability"] == 40
    # FTO exposure deterministic default
    assert gauges["FTO Exposure"] == 30
    # Strategic moat deterministic default
    assert gauges["Strategic Moat"] == 20
    # confidence trail mentions hash prefix + counts
    assert "1 claim genome" in metrics["confidence_trail"]
    assert "1 prior-art collision" in metrics["confidence_trail"]


def test_derive_metrics_no_collisions_zero_vulnerability():
    cir = json.loads(json.dumps(MINIMAL_CIR))
    cir["claims"][0]["elements"][0]["prior_art_collisions"] = []
    metrics = rd.derive_metrics(cir, None)
    vuln = next(g for g in metrics["gauges"] if g["label"] == "Prior-Art Vulnerability")
    assert vuln["score"] == 0
    assert "no prior-art collisions identified" in vuln["basis"]


def test_tier_weights_are_complete():
    assert rd.TIER_WEIGHTS["Tier 1: Anticipation Candidate"] == 1.0
    assert rd.TIER_WEIGHTS["Tier 5: Hidden Prior Art"] == 0.5
    assert len(rd.TIER_WEIGHTS) == 5


def test_vulnerability_labels():
    assert rd._vulnerability(85) == "High"
    assert rd._vulnerability(40) == "Moderate"
    assert rd._vulnerability(10) == "Low"


def test_status_file_populates_family_and_verdict(tmp_path, cir_file):
    status = tmp_path / "status.json"
    status.write_text(json.dumps({
        "filing_date": "2001-06-01",
        "grant_date": "2003-01-14",
        "status": {"state": "Expired - Lifetime"},
        "family": {"applications": [{"application": "US09/872,528"}]},
        "forward_citations": [{"publication": "US-1-A", "assignee": "Acme", "title": "t"}],
    }), encoding="utf-8")
    html = rd.render_dossier(cir_file, status_path=status)
    assert "Filed 2001-06-01" in html
    assert "Expired - Lifetime" in html
    assert "Acme" in html
    assert "grant Expired - Lifetime" in html  # verdict basis reflects real status
