"""Coverage gates.

v1.7 accepted substitutions where the framework required something stronger:

  * a single source where >= 2 were required
  * Crossref where a domain-specific source was required
  * a NAICS code where a bounded market model was required
  * a candidate list where a partner-fit analysis was required
  * six references mapped where the complete cited set was required
  * a skipped domain-orientation stage

Each of those is a *coverage* defect, not a judgment call. These gates make
them machine-enforceable so a downstream scorer cannot treat a substitution
as if the required evidence had been gathered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceRequirement:
    """One required source for an avenue's coverage."""

    source: str                 # e.g. "google_patents"
    minimum: int = 1
    aliases: tuple[str, ...] = ()   # acceptable substitute identities


@dataclass(frozen=True)
class CoverageGate:
    """A coverage gate with a machine-checkable rule."""

    name: str
    required_sources: tuple[SourceRequirement, ...]
    required_fields: tuple[str, ...] = ()
    minimum_attempts: int = 1
    description: str = ""

    def check(
        self,
        attempts: list[dict[str, Any]],
        support: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        errors: list[str] = []
        used = {a.get("source", "") for a in attempts}
        for req in self.required_sources:
            satisfied = req.source in used or any(
                alias in used for alias in req.aliases
            )
            if not satisfied:
                errors.append(
                    f"{self.name}: required source '{req.source}' not used "
                    f"(aliases: {list(req.aliases) or 'none'})")
        if len(attempts) < self.minimum_attempts:
            errors.append(
                f"{self.name}: {len(attempts)} attempts < required "
                f"{self.minimum_attempts}")
        if self.required_fields:
            # The required schema fields must be present on at least one
            # support object. A substitution (NAICS code for a bounded market
            # model, candidate list for a partner-fit analysis) fails here
            # because the required field is absent from every support object.
            fields_found: set[str] = set()
            for obj in support or []:
                fields_found |= {
                    k for k, v in obj.items()
                    if v not in (None, "", [], {},)
                }
            missing = [f for f in self.required_fields if f not in fields_found]
            if missing:
                errors.append(
                    f"{self.name}: required schema fields absent from all "
                    f"support objects: {missing}")
        return errors


# ---------------------------------------------------------------------------
# Per-avenue gates
# ---------------------------------------------------------------------------

PATENT_COVERAGE = CoverageGate(
    name="patent_coverage",
    required_sources=(
        SourceRequirement("google_patents", aliases=("primary_patent_database",)),
        SourceRequirement("espacenet", aliases=("secondary_patent_database",)),
    ),
    minimum_attempts=2,
    description="Patent avenues require at least two independent databases.",
)

LITERATURE_COVERAGE = CoverageGate(
    name="literature_coverage",
    required_sources=(
        SourceRequirement("crossref", aliases=("doi_database",)),
        SourceRequirement("scholarly_database", aliases=("pubmed", "semantic_scholar")),
        SourceRequirement("technical_database", aliases=("engineering_database",)),
    ),
    minimum_attempts=2,
    description="Literature avenues require a scholarly database AND a "
                "domain-specific technical database; Crossref alone is a "
                "locator, not a domain source.",
)

MARKET_COVERAGE = CoverageGate(
    name="market_coverage",
    required_sources=(
        SourceRequirement("public_health_source", aliases=("pubmed",)),
        SourceRequirement("industry_source", aliases=("census", "industry_database")),
    ),
    required_fields=("market_boundary", "geography", "time_period", "figure",
                     "source", "derivation"),
    minimum_attempts=2,
    description="Market avenues require a bounded market model with "
                "market_boundary, geography, time_period, figure, source, and "
                "derivation. A NAICS code alone is not a market model.",
)

PARTNER_COVERAGE = CoverageGate(
    name="partner_coverage",
    required_sources=(
        SourceRequirement("assignment_source", aliases=("patent_assignment",)),
        SourceRequirement("company_source", aliases=("company_database",)),
    ),
    required_fields=("organization", "sells", "buys", "technical_need",
                     "invention_mapping"),
    minimum_attempts=1,
    description="Partner avenues require a partner_fit analysis with "
                "organization, sells, buys, technical_need, and "
                "invention_mapping. A candidate list is not a fit analysis.",
)

NOVELTY_COVERAGE = CoverageGate(
    name="novelty_coverage",
    required_sources=(
        SourceRequirement("google_patents", aliases=("primary_patent_database",)),
        SourceRequirement("espacenet", aliases=("secondary_patent_database",)),
    ),
    required_fields=("claim_element_mapping",),
    minimum_attempts=2,
    description="Novelty avenues require a complete claim-to-reference "
                "mapping, not a partial subset.",
)

TECHNOLOGY_COVERAGE = CoverageGate(
    name="technology_coverage",
    required_sources=(
        SourceRequirement("patent_specification", aliases=("primary_source",)),
    ),
    required_fields=("feature_to_benefit", "domain_orientation"),
    minimum_attempts=1,
    description="Technology avenues require an explicit domain orientation "
                "stage; skipping it is a process defect.",
)

ALL_GATES: tuple[CoverageGate, ...] = (
    PATENT_COVERAGE, LITERATURE_COVERAGE, MARKET_COVERAGE,
    PARTNER_COVERAGE, NOVELTY_COVERAGE, TECHNOLOGY_COVERAGE,
)


def gate_by_name(name: str) -> CoverageGate:
    for gate in ALL_GATES:
        if gate.name == name:
            return gate
    raise KeyError(f"unknown coverage gate: {name}")


@dataclass
class CoverageReport:
    gate: str
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {"gate": self.gate, "passed": self.passed, "errors": self.errors}


def run_coverage_gate(
    gate: CoverageGate,
    attempts: list[dict[str, Any]],
    support: list[dict[str, Any]] | None = None,
) -> CoverageReport:
    return CoverageReport(gate=gate.name, errors=gate.check(attempts, support))


def run_all_coverage_gates(
    avenue_attempts: dict[str, list[dict[str, Any]]],
    avenue_support: dict[str, list[dict[str, Any]]] | None = None,
) -> list[CoverageReport]:
    """Run every declared gate against its avenue's attempts and support.

    ``avenue_attempts`` maps a gate name to the list of recovery attempts
    recorded for that avenue. ``avenue_support`` maps a gate name to the list
    of evidence-support objects gathered. Avenues with no attempts are
    reported as failing their minimum-attempts rule.
    """
    avenue_support = avenue_support or {}
    reports: list[CoverageReport] = []
    for gate in ALL_GATES:
        attempts = avenue_attempts.get(gate.name, [])
        support = avenue_support.get(gate.name, [])
        reports.append(run_coverage_gate(gate, attempts, support))
    return reports


def coverage_blocker_messages(reports: list[CoverageReport]) -> list[str]:
    messages: list[str] = []
    for report in reports:
        for error in report.errors:
            messages.append(error)
    return messages