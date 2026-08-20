"""Hermetic mocked live adapters preserving source distinctions.

Each source type returns a distinct, realistic payload so the pipeline can
be exercised without live network access:

  patent HTML      → Google Patents page with patent_id in title/claims
  crossref JSON    → literature items with DOI, authors, venue
  worldbank JSON   → population proxy observations
  partner HTML     → publication numbers/titles
  recovery bins    → strategy-specific binary blobs

Never a single generic fake response for every source type.
"""

from __future__ import annotations

import json
from typing import Callable


def make_hermetic_fetcher(patent_id: str = "US8527057") -> Callable[[str], bytes]:
    normalized = patent_id.upper()

    def fetcher(url: str) -> bytes:
        if "patents.google.com/patent/" in url and "/en" in url:
            # Extract requested patent ID from URL
            pid = url.split("/patent/")[1].split("/")[0]
            return f"""<html><head></head><body>
            <div itemprop="title">Hermetic Patent {pid}</div>
            <div class="claim-text">1. A retinal prosthesis comprising an electrode array, a scleral strap, a hermetic package.</div>
            <table><tr itemprop="countryStatus"><td itemprop="documentId">{pid}</td><td itemprop="legalStatus">Active</td></tr></table>
            <tr itemprop="docdbFamily"><td itemprop="publicationNumber">US7881799B2</td></tr>
            <tr itemprop="backwardReferences"><td itemprop="publicationNumber">US7651865B2</td></tr>
            <tr itemprop="forwardReferences"><td itemprop="publicationNumber">US20110118807A1</td></tr>
            </body></html>""".encode("utf-8")

        if "api.crossref.org/works" in url:
            return json.dumps({
                "message": {
                    "items": [
                        {
                            "author": [{"family": "Hermetic", "given": "Alice"}],
                            "title": [f"Study of {normalized} Technology"],
                            "container-title": ["Journal of Hermetic Testing"],
                            "published": {"date-parts": [[2023, 1, 15]]},
                            "DOI": f"10.1234/hermetic.{normalized.lower()}",
                            "URL": "https://doi.org/10.1234/hermetic",
                        },
                        {
                            "author": [{"family": "Mock", "given": "Bob"}],
                            "title": ["Retinal Prosthesis Long-Term Study"],
                            "container-title": ["Nature Hermetic"],
                            "published": {"date-parts": [[2022, 6, 1]]},
                            "DOI": "10.5678/mock.retinal",
                            "URL": "https://doi.org/10.5678/mock",
                        },
                    ]
                }
            }).encode("utf-8")

        if "worldbank.org" in url or "SP.POP.TOTL" in url:
            return json.dumps([
                {"page": 1, "pages": 1},
                [
                    {"date": "2020", "value": 7800000000},
                    {"date": "2021", "value": 7900000000},
                ],
            ]).encode("utf-8")

        if "patents.google.com/?q=" in url:
            # Partner / recovery / troubleshooting queries
            query = url.split("?q=")[1] if "?q=" in url else "generic"
            # Return HTML with publication numbers
            return f"""<html><body>
            <tr itemprop="publicationNumber">US7651865B2</tr><div itemprop="title">Hermetic Partner Device for {query[:30]}</div>
            <tr itemprop="publicationNumber">US20150012345A1</tr><div itemprop="title">Hermetic System for {query[:30]}</div>
            </body></html>""".encode("utf-8")

        if "patents.google.com" in url:
            return b"<html><body>generic patent search results</body></html>"

        # Recovery bins: any other URL is a recovery strategy
        return f"hermetic recovery blob for {url[:80]}".encode("utf-8")

    return fetcher
