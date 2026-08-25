# Test-report-results/tests_v17/test_claims.py
import pytest
from engine_v17.claims import SourceType, QuantitativeClaim, parse_claims
from engine_v17.models import EpistemicState, Scope


def test_source_type_has_all_six_values():
    assert {s.value for s in SourceType} == {
        "LLM_INFERENCE", "INDUSTRY_BENCHMARK", "STRUCTURED_DATABASE",
        "COMPANY_REPORTED", "REGULATORY_RECORD", "PEER_REVIEWED",
    }


def test_quantitative_claim_round_trip():
    c = QuantitativeClaim(
        claim_id="Q-07-001",
        proposition_id="P-07-001",
        metric="BCI total addressable market",
        value="~$3.25B",
        unit="USD",
        source_type=SourceType.LLM_INFERENCE,
        source="LLM synthesis of industry reports",
        date="2026-08-19",
        population="global BCI devices + intracortical electrodes + neuroprosthetics + visual prostheses",
        comparison_group="none",
        scope=Scope.MARKET,
        epistemic_state=EpistemicState.NOT_ESTABLISHED,
        confidence="LOW",
        note="Directional only; no structured market database consulted",
    )
    d = c.to_dict()
    assert d["source_type"] == "LLM_INFERENCE"
    assert d["epistemic_state"] == "NOT_ESTABLISHED"
    assert d["scope"] == "MARKET"
    c2 = QuantitativeClaim.from_dict(d)
    assert c2 == c


def test_parse_claims_requires_source_type():
    with pytest.raises(ValueError):
        parse_claims([{"claim_id": "Q-07-002", "metric": "CAGR", "value": "14.5%"}])