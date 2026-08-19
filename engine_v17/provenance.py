"""Provenance invariants for queries, charts, and time-bucketed inference."""

from dataclasses import dataclass
import hashlib
import re


@dataclass(frozen=True)
class QueryProvenance:
    query_id: str
    canonical_query: str
    source: str
    result_count: int | None
    date_as_of: str | None = None
    query_hash: str = ""

    def __post_init__(self):
        if not self.query_hash:
            object.__setattr__(self, "query_hash", hashlib.sha256(self.canonical_query.encode()).hexdigest()[:16])


def validate_query_match(narrative_query: str, chart_query: str) -> list[str]:
    normalize = lambda value: re.sub(r"\s+", " ", value.strip().lower())
    if normalize(narrative_query) != normalize(chart_query):
        return ["narrative_query_does_not_match_chart_query"]
    return []


def validate_time_bucket_labels(labels: list[str], as_of: str) -> list[str]:
    year = int(as_of[:4])
    errors = []
    for label in labels:
        years = [int(x) for x in re.findall(r"20\d{2}", label)]
        if years and max(years) > year:
            errors.append(f"future_bucket:{label}")
        if years and max(years) == year and ("YTD" not in label.upper() and "TO_DATE" not in label.upper()):
            errors.append(f"current_partial_bucket_not_marked:{label}")
    return errors
