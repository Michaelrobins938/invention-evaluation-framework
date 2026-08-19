from engine_v17.rights_graph import build_rights_graph, legal_leverage


def test_expired_us8527057_blocks_standalone_licensing():
    graph = build_rights_graph([{
        "patent": "US8527057B2",
        "status": {"active": False, "state": "EXPIRED", "reason": "maintenance_fee_nonpayment"},
        "assignments": [{"assignee": "Cortigent", "date": 2023}],
    }])
    leverage = legal_leverage(graph)
    assert leverage.state == "minimal"
    assert "standalone_patent_licensing_blocked" in leverage.constraints


def test_expired_target_does_not_hide_active_family_members():
    graph = build_rights_graph([{
        "patent": "US8527057B2",
        "family": {"members": [
            {"patent": "US7881799B2", "state": "ACTIVE"},
            {"patent": "US8473048B2", "state": "ACTIVE"},
        ]},
        "status": {"active": False, "state": "EXPIRED"},
    }])
    assert [m["patent"] for m in graph.family["members"]] == ["US7881799B2", "US8473048B2"]
