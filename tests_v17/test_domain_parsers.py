import json

from engine_v17.domain_parsers import (
    parse_crossref_literature,
    parse_market_proxy,
    parse_partner_candidates,
    parse_patent_metadata,
    parse_patent_claims,
)


def test_patent_parser_extracts_identity_family_status_and_citations():
    html = """
    <meta scheme="dateSubmitted" content="2008-10-13">
    <meta scheme="datePublished" content="2014-12-09">
    <span itemprop="title">Locomotion Assisting Device</span>
    <tr itemprop="docdbFamily"><td itemprop="publicationNumber">US8096965B2</td></tr>
    <tr itemprop="countryStatus"><td itemprop="documentId">US8905955B2</td><td itemprop="legalStatus">Active</td></tr>
    <tr itemprop="backwardReferences"><td itemprop="publicationNumber">US7153242B2</td></tr>
    """
    parsed = parse_patent_metadata(html, "US8905955B2")
    assert parsed["patent_id"] == "US8905955B2"
    assert parsed["family_members"] == ["US8096965B2"]
    assert parsed["status"][0]["state"] == "Active"
    assert parsed["backward_references"] == ["US7153242B2"]


def test_patent_parser_extracts_claim_limitation_text():
    html = '<div class="claim"><div class="claim-text">1. A method comprising sensing force;</div><div class="claim-text">actuating a joint.</div></div>'
    claims = parse_patent_claims(html)
    assert claims[0]["claim_number"] == "1"
    assert "sensing force" in claims[0]["text"]
    assert len(claims[0]["limitations"]) == 2


def test_crossref_parser_preserves_identity_and_marks_missing_fields():
    payload = {"message": {"items": [{"title": ["Exoskeleton control"], "DOI": "10.1234/test", "author": [{"family": "Doe"}]}]}}
    records = parse_crossref_literature(json.dumps(payload).encode())
    assert records[0]["title"] == "Exoskeleton control"
    assert records[0]["doi_or_report_number"] == "10.1234/test"
    assert records[0]["authors"] == ["Doe"]
    assert records[0]["missing_fields"]


def test_market_parser_is_a_proxy_not_a_market_size_finding():
    payload = b'[{"page":1},{"date":"2024","value":100}]'
    parsed = parse_market_proxy(payload)
    assert parsed["proxy_type"] == "population"
    assert parsed["market_sizing_admissible"] is False
    assert parsed["observations"][0]["value"] == 100


def test_partner_parser_returns_candidates_without_claiming_fit():
    html = '<span itemprop="publicationNumber">US1234567A</span><span itemprop="title">Mobility exoskeleton</span>'
    candidates = parse_partner_candidates(html.encode())
    assert candidates[0]["publication_number"] == "US1234567A"
    assert candidates[0]["partner_fit_state"] == "WORK QUEUE"
