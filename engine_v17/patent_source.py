"""Extract structured patent-page tables instead of treating a fetch as a read."""

from __future__ import annotations

import html as html_lib
import re
from typing import Any


def _text(block: str, prop: str) -> str | None:
    match = re.search(rf'itemprop="{re.escape(prop)}"[^>]*>(.*?)</', block, re.S)
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub("<[^>]+>", "", match.group(1)))).strip() if match else None


def _rows(source: str, row_prop: str) -> list[dict[str, Any]]:
    rows = []
    for block in re.findall(rf'<tr itemprop="{row_prop}"[^>]*>(.*?)</tr>', source, re.S):
        number = _text(block, "publicationNumber")
        if number:
            rows.append({
                "publication_number": number,
                "priority_date": _text(block, "priorityDate"),
                "publication_date": _text(block, "publicationDate"),
                "assignee": _text(block, "assigneeOriginal"),
                "title": _text(block, "title"),
                "examiner_cited": 'itemprop="examinerCited"' in block,
                "third_party_cited": 'itemprop="thirdPartyCited"' in block,
            })
    return rows


def extract_patent_page(source: str) -> dict[str, Any]:
    family = []
    for block in re.findall(r'<tr itemprop="docdbFamily"[^>]*>(.*?)</tr>', source, re.S):
        number = _text(block, "publicationNumber")
        if number:
            family.append({"publication_number": number, "publication_date": _text(block, "publicationDate")})
    statuses = []
    for block in re.findall(r'<tr itemprop="countryStatus"[^>]*>(.*?)</tr>', source, re.S):
        number = _text(block, "documentId") or _text(block, "publicationNumber")
        if number:
            statuses.append({
                "publication_number": number,
                "state": _text(block, "legalStatus"),
                "category": _text(block, "legalStatusCat"),
                "expiration": _text(block, "ifiExpiration"),
            })
    backward = _rows(source, "backwardReferences") or _rows(source, "backwardReferencesOrig")
    forward_family = _rows(source, "forwardReferencesFamily")
    forward = (
        _rows(source, "forwardReferences")
        + _rows(source, "forwardReferencesOrig")
        + forward_family
    )
    return {
        "backward_references": backward,
        "forward_references": forward,
        "forward_citing_families": forward_family,
        "family": family,
        "country_status": statuses,
        "counts": {
            "backward_references": len(backward),
            "forward_references": len(forward),
            "forward_citing_families": len(forward_family),
            "family_members": len(family),
        },
    }
