"""Retrieval, normalization, and inference separation for landscapes."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalSet:
    query: dict[str, Any]
    records: list[dict[str, Any]]


@dataclass
class NormalizedLandscape:
    query: dict[str, Any]
    families: list[list[dict[str, Any]]] = field(default_factory=list)
    normalized_assignees: dict[str, int] = field(default_factory=dict)
    relevance: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class LandscapeInference:
    retrieval_count: int
    normalized_family_count: int
    decision_value: str
    findings: list[str]


def record_retrieval(records: list[dict[str, Any]], query: dict[str, Any]) -> RetrievalSet:
    return RetrievalSet(query=query, records=list(records))


def normalize_landscape(retrieval: RetrievalSet) -> NormalizedLandscape:
    groups: dict[str, list[dict[str, Any]]] = {}
    assignees: dict[str, int] = {}
    relevance: dict[str, dict[str, Any]] = {}
    for record in retrieval.records:
        family = record.get("family_id", record.get("publication_number", "unknown"))
        groups.setdefault(family, []).append(record)
        assignee = record.get("assignee", "unknown").strip().lower()
        assignees[assignee] = assignees.get(assignee, 0) + 1
        relevance[record.get("publication_number", family)] = record.get(
            "relevance", {"direct": False, "adjacent": True, "contextual": False, "decision_value": "low"}
        )
    return NormalizedLandscape(retrieval.query, list(groups.values()), assignees, relevance)


def infer_landscape(landscape: NormalizedLandscape) -> LandscapeInference:
    direct = sum(1 for r in landscape.relevance.values() if r.get("direct"))
    value = "high" if direct else "low"
    return LandscapeInference(
        retrieval_count=sum(len(group) for group in landscape.families),
        normalized_family_count=len(landscape.families),
        decision_value=value,
        findings=["raw retrieval volume is not equivalent to competitive asset count"],
    )
