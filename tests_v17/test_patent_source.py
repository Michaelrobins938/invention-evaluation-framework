from engine_v17.patent_source import extract_patent_page


def test_patent_source_extractor_keeps_examiner_citation_flag():
    html = '''<tr itemprop="backwardReferencesOrig"><td><span itemprop="publicationNumber">US20050222624A1</span><span itemprop="examinerCited">*</span></td><td itemprop="title">Side coil</td></tr>'''
    result = extract_patent_page(html)
    assert result["backward_references"][0]["examiner_cited"] is True


def test_patent_source_extractor_counts_family_and_forward_rows():
    html = '''<tr itemprop="docdbFamily"><td><span itemprop="publicationNumber">US7881799B2</span></td></tr><tr itemprop="forwardReferences"><td><span itemprop="publicationNumber">US9555244B2</span></td></tr>'''
    result = extract_patent_page(html)
    assert result["counts"] == {"backward_references": 0, "forward_references": 1, "forward_citing_families": 0, "family_members": 1}
