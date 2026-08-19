"""Domain parsers that turn live adapter responses into typed candidate objects."""

from __future__ import annotations

import html as html_lib
import json
import re
from typing import Any


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def _rows(source: str, row_prop: str) -> list[str]:
    values = []
    for block in re.findall(rf'<tr itemprop="{re.escape(row_prop)}"[^>]*>(.*?)</tr>', source, re.S):
        match = re.search(r'itemprop="publicationNumber"[^>]*>(.*?)</', block, re.S)
        if match:
            values.append(_clean(match.group(1)))
    return values


def parse_patent_metadata(source: str, patent_id: str) -> dict[str, Any]:
    title_match = re.search(r'itemprop="title"[^>]*>(.*?)</', source, re.S)
    statuses = []
    for block in re.findall(r'<tr itemprop="countryStatus"[^>]*>(.*?)</tr>', source, re.S):
        document = re.search(r'itemprop="documentId"[^>]*>(.*?)</', block, re.S)
        state = re.search(r'itemprop="legalStatus"[^>]*>(.*?)</', block, re.S)
        statuses.append({
            "document_id": _clean(document.group(1)) if document else "",
            "state": _clean(state.group(1)) if state else "",
        })
    return {
        "patent_id": patent_id,
        "title": _clean(title_match.group(1)) if title_match else "",
        "family_members": _rows(source, "docdbFamily"),
        "status": statuses,
        "backward_references": _rows(source, "backwardReferences"),
        "forward_references": _rows(source, "forwardReferences"),
    }


def parse_patent_claims(source: str) -> list[dict[str, Any]]:
    """Extract claim text and sentence-level limitation candidates from patent HTML."""
    claims: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in re.findall(r'<div class="claim-text"[^>]*>(.*?)</div>', source, re.S):
        text = _clean(raw)
        number_match = re.match(r"(\d+)\.\s*", text)
        if number_match:
            if current:
                claims.append(current)
            current = {"claim_number": number_match.group(1), "parts": [text]}
        elif current:
            current["parts"].append(text)
    if current:
        claims.append(current)
    return [
        {
            "claim_number": claim["claim_number"],
            "text": " ".join(claim["parts"]),
            "limitations": [part.strip(" ;") for part in claim["parts"] if part.strip(" ;")],
        }
        for claim in claims
    ]


def parse_crossref_literature(payload: bytes) -> list[dict[str, Any]]:
    data = json.loads(payload.decode("utf-8"))
    items = data.get("message", {}).get("items", [])
    records = []
    required = ("authors", "title", "venue", "date", "doi_or_report_number", "url", "experimental_system", "technology", "application", "demonstrated_result", "relevance")
    for item in items:
        authors = [author.get("family", "") for author in item.get("author", []) if author.get("family")]
        title = (item.get("title") or [""])[0]
        doi = item.get("DOI", "")
        records.append({
            "authors": authors,
            "title": title,
            "venue": item.get("container-title", [""])[0] if item.get("container-title") else "",
            "date": str(item.get("published", {}).get("date-parts", [[""]])[0][0]),
            "doi_or_report_number": doi,
            "url": item.get("URL", ""),
            "experimental_system": "",
            "technology": "",
            "application": "",
            "demonstrated_result": "",
            "relevance": "",
            "missing_fields": [field for field in required if not {
                "authors": authors, "title": title, "venue": item.get("container-title", [""])[0] if item.get("container-title") else "", "date": str(item.get("published", {}).get("date-parts", [[""]])[0][0]), "doi_or_report_number": doi, "url": item.get("URL", ""), "experimental_system": "", "technology": "", "application": "", "demonstrated_result": "", "relevance": ""
            }.get(field)],
        })
    return records


def parse_market_proxy(payload: bytes) -> dict[str, Any]:
    data = json.loads(payload.decode("utf-8"))
    rows = data[1] if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list) else data
    observations = []
    for row in rows if isinstance(rows, list) else []:
        if isinstance(row, dict) and "value" in row:
            observations.append({"date": row.get("date", ""), "value": row.get("value")})
    return {
        "proxy_type": "population",
        "observations": observations,
        "market_sizing_admissible": False,
        "reason": "population proxy is not a reconstructable market-size proposition",
    }


def parse_partner_candidates(source: bytes) -> list[dict[str, Any]]:
    text = source.decode("utf-8", "ignore")
    numbers = re.findall(r'itemprop="publicationNumber"[^>]*>(.*?)</', text, re.S)
    titles = re.findall(r'itemprop="title"[^>]*>(.*?)</', text, re.S)
    candidates = []
    for index, number in enumerate(numbers):
        candidates.append({
            "publication_number": _clean(number),
            "title": _clean(titles[index]) if index < len(titles) else "",
            "partner_fit_state": "WORK QUEUE",
            "missing_fields": ["organization", "sells", "buys", "technical_need", "invention_mapping"],
        })
    return candidates
