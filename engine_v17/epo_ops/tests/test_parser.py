"""Tests for EPO OPS XML parser."""

from __future__ import annotations

import pytest

from engine_v17.epo_ops.models import (
    CitationCategory,
    CitedBy,
    CitedPhase,
    NplCitation,
    PatentCitation,
)
from engine_v17.epo_ops.parser import (
    _parse_citation_category,
    _parse_npl_citation_text,
    parse_bibliographic_xml,
    parse_search_xml,
)


# Minimal EPO OPS bibliographic XML with both patcit and nplcit
_SAMPLE_BIBLIO_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ops:world-patent-data xmlns:ops="http://ops.epo.org">
  <ops:patent-document>
    <ops:citations>
      <ops:citation cited-by="examiner" cited-phase="search">
        <ops:category>X</ops:category>
        <ops:patcit>
          <ops:document-id>
            <ops:doc-number>US1234567</ops:doc-number>
            <ops:date>20000101</ops:date>
            <ops:title>Prior Art Reference</ops:title>
          </ops:document-id>
        </ops:patcit>
      </ops:citation>
      <ops:citation cited-by="examiner" cited-phase="search">
        <ops:category>X</ops:category>
        <ops:nplcit>
          <ops:text>Smith, J. Advanced Neural Interfaces. Journal of Neuroscience. 2015.</ops:text>
        </ops:nplcit>
      </ops:citation>
      <ops:citation cited-by="applicant" cited-phase="examination">
        <ops:category>A</ops:category>
        <ops:patcit>
          <ops:document-id>
            <ops:doc-number>EP9876543</ops:doc-number>
            <ops:date>20050101</ops:date>
            <ops:title>Related Technology</ops:title>
          </ops:document-id>
        </ops:patcit>
      </ops:citation>
    </ops:citations>
  </ops:patent-document>
</ops:world-patent-data>
"""

# XML with XP number in NPL citation
_SAMPLE_XP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ops:world-patent-data xmlns:ops="http://ops.epo.org">
  <ops:patent-document>
    <ops:citations>
      <ops:citation cited-by="examiner" cited-phase="search">
        <ops:category>X</ops:category>
        <ops:nplcit>
          <ops:text>Doe, J. Brain-Computer Interfaces. XP000123456. 2010.</ops:text>
        </ops:nplcit>
      </ops:citation>
    </ops:citations>
  </ops:patent-document>
</ops:world-patent-data>
"""

# XML with no citations
_SAMPLE_NO_CITATIONS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ops:world-patent-data xmlns:ops="http://ops.epo.org">
  <ops:patent-document>
    <ops:citations />
  </ops:patent-document>
</ops:world-patent-data>
"""

# Sample search results XML
_SAMPLE_SEARCH_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ops:world-patent-data xmlns:ops="http://ops.epo.org">
  <ops:search-result>
    <ops:publication-reference>
      <ops:document-id>
        <ops:epodoc>US5215088</ops:epodoc>
        <ops:doc-number>5215088</ops:doc-number>
        <ops:date>19930406</ops:date>
      </ops:document-id>
    </ops:publication-reference>
    <ops:title>Three-Dimensional Electrode Device</ops:title>
  </ops:search-result>
  <ops:search-result>
    <ops:publication-reference>
      <ops:document-id>
        <ops:epodoc>EP1234567</ops:epodoc>
        <ops:doc-number>1234567</ops:doc-number>
        <ops:date>20050101</ops:date>
      </ops:document-id>
    </ops:publication-reference>
    <ops:title>Related Patent</ops:title>
  </ops:search-result>
</ops:world-patent-data>
"""


class TestParseCitationCategory:
    def test_single_category(self):
        result = _parse_citation_category("X")
        assert result == [CitationCategory.X]

    def test_multiple_categories(self):
        result = _parse_citation_category("XY")
        assert result == [CitationCategory.X, CitationCategory.Y]

    def test_same_family(self):
        result = _parse_citation_category("&")
        assert result == [CitationCategory.SAME_FAMILY]

    def test_plus_combination(self):
        result = _parse_citation_category("+")
        assert result == [CitationCategory.PLUS]

    def test_empty_string(self):
        result = _parse_citation_category("")
        assert result == []

    def test_none_input(self):
        result = _parse_citation_category(None)
        assert result == []

    def test_unknown_characters_ignored(self):
        result = _parse_citation_category("XZ")
        assert result == [CitationCategory.X]


class TestParseNplCitationText:
    def test_standard_format(self):
        result = _parse_npl_citation_text(
            "Smith, J. Advanced Neural Interfaces. Journal of Neuroscience. 2015."
        )
        assert result["title"] == "Advanced Neural Interfaces"
        assert "Smith, J" in result["authors"]
        assert result["source_publication"] == "Journal of Neuroscience"
        assert result["publication_date"] == "2015"

    def test_semicolon_delimited(self):
        result = _parse_npl_citation_text(
            "Smith, J.; Doe, J. Test Article. Nature. 2020."
        )
        assert len(result["authors"]) == 2
        assert result["title"] == "Test Article"

    def test_empty_text(self):
        result = _parse_npl_citation_text("")
        assert result["authors"] == []
        assert result["title"] is None

    def test_none_input(self):
        result = _parse_npl_citation_text(None)
        assert result["authors"] == []


class TestParseBibliographicXml:
    def test_parses_patent_citations(self):
        bundle = parse_bibliographic_xml(_SAMPLE_BIBLIO_XML, "US5215088A")
        assert len(bundle.patcit) == 2
        assert bundle.patcit[0].publication_number == "US1234567"
        assert bundle.patcit[0].title == "Prior Art Reference"
        assert bundle.patcit[0].examiner_cited is True
        assert bundle.patcit[0].cited_phase == CitedPhase.SEARCH

    def test_parses_npl_citations(self):
        bundle = parse_bibliographic_xml(_SAMPLE_BIBLIO_XML, "US5215088A")
        assert len(bundle.nplcit) == 1
        npl = bundle.nplcit[0]
        assert "Smith, J" in npl.authors
        assert npl.cited_by == CitedBy.EXAMINER
        assert npl.cited_phase == CitedPhase.SEARCH
        assert CitationCategory.X in npl.citation_categories

    def test_parses_xp_number(self):
        bundle = parse_bibliographic_xml(_SAMPLE_XP_XML, "US5215088A")
        assert len(bundle.nplcit) == 1
        assert bundle.nplcit[0].xp_number == "XP000123456"

    def test_no_citations(self):
        bundle = parse_bibliographic_xml(_SAMPLE_NO_CITATIONS_XML, "US5215088A")
        assert len(bundle.patcit) == 0
        assert len(bundle.nplcit) == 0

    def test_retrieval_metadata(self):
        bundle = parse_bibliographic_xml(_SAMPLE_BIBLIO_XML, "US5215088A")
        assert bundle.retrieval_metadata["patent_number"] == "US5215088A"
        assert bundle.retrieval_metadata["patcit_count"] == 2
        assert bundle.retrieval_metadata["nplcit_count"] == 1

    def test_bytes_input(self):
        bundle = parse_bibliographic_xml(
            _SAMPLE_BIBLIO_XML.encode("utf-8"), "US5215088A"
        )
        assert len(bundle.patcit) == 2


class TestParseSearchXml:
    def test_parses_search_results(self):
        results = parse_search_xml(_SAMPLE_SEARCH_XML)
        assert len(results) == 2
        assert results[0]["publication_number"] == "5215088"
        assert results[0]["title"] == "Three-Dimensional Electrode Device"
        assert results[1]["publication_number"] == "1234567"

    def test_empty_search_results(self):
        empty_xml = """<?xml version="1.0"?>
        <ops:world-patent-data xmlns:ops="http://ops.epo.org">
        </ops:world-patent-data>"""
        results = parse_search_xml(empty_xml)
        assert results == []