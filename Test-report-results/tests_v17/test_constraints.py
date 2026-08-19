from engine_v17.constraints import calculate_evidence_debt, propagate_constraints
from engine_v17.models import Proposition


def test_incomplete_prior_art_caps_ip_and_patentability():
    propositions = [Proposition(
        id="P-05-001", claim="anticipation", downstream_effects=["anticipation"],
        search_completeness="incomplete",
    )]
    targets = {c.target for c in propagate_constraints(propositions)}
    assert {"patentability_confidence", "ip_leverage"} <= targets


def test_evidence_debt_prioritizes_patent_blocker():
    propositions = [
        Proposition(id="P-08-001", downstream_effects=["partner_fit"]),
        Proposition(id="P-05-001", downstream_effects=["anticipation"]),
    ]
    assert calculate_evidence_debt(propositions)[0].proposition_id == "P-05-001"
