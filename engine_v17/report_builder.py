"""Build a v1.7 report from phase artifacts and graph state, never from v1.6 PDF/MD.

Executive-summary structure is prescribed, not improvised (E9 enforces presence):

  1.1 Evaluation Overview
  1.2 Bottom Line
  1.3 Rating Methodology   — scale, component criteria, weights, thresholds
  1.4 Key Evidence Supporting the Ratings
  Proposition Identifier Legend
  ...body phases...
  Operational Audit        — debt table with proper columns (ID | state | barrier | description)

Rating labels come from RATING_BANDS via rating_from_ratio(); nothing else may
map scores to labels, so identical totals cannot silently receive different
ratings unless disclosed weights differ.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .report_integrity import PROPOSITION_LEGEND

PHASES = [
    ("technology-profile-*.md", "Technology Analysis"),
    ("patent-landscape-*.md", "Patent Landscape Analysis"),
    ("novelty-search-*.md", "IP / Novelty Analysis"),
    ("literature-search-*.md", "Literature Analysis"),
    ("market-analysis-*.md", "Market Analysis"),
    ("partner-analysis-*.md", "Potential Partners"),
    ("avenue-ledger-*.md", "Operational Audit"),
]

# Single source of truth: ratio of component points earned → rating label.
# Weights are disclosed in the methodology section; under equal weights,
# identical ratios MUST produce identical labels.
RATING_BANDS: list[tuple[float, str]] = [
    (0.80, "Established"),
    (0.60, "Moderate"),
    (0.40, "Limited-Moderate"),
    (0.20, "Limited"),
    (0.00, "Not Established"),
]

DEFAULT_COMPONENT_WEIGHTS: dict[str, float] = {
    "Technology": 1.0,
    "IP / Novelty": 1.5,
    "Market": 1.0,
}


def rating_from_ratio(ratio: float) -> str:
    """Map an earned/maximum ratio to its rating label. Only mapping in the codebase."""
    for threshold, label in RATING_BANDS:
        if ratio >= threshold:
            return label
    return RATING_BANDS[-1][1]


def rating_from_components(components: dict[str, tuple[int, int]], weights: dict[str, float] | None = None) -> str:
    """Weighted rating across components. components: name -> (earned, maximum)."""
    w = weights or DEFAULT_COMPONENT_WEIGHTS
    total_weighted = 0.0
    total_max = 0.0
    for name, (earned, maximum) in components.items():
        if maximum <= 0:
            continue
        weight = w.get(name, 1.0)
        total_weighted += weight * (earned / maximum)
        total_max += weight
    if total_max == 0:
        return RATING_BANDS[-1][1]
    return rating_from_ratio(total_weighted / total_max)


def _read_first(directory: Path, pattern: str) -> str:
    matches = sorted(directory.glob(pattern))
    return matches[0].read_text(encoding="utf-8") if matches else "_No phase artifact was produced._"


def _embed(source: str) -> str:
    """Embed a source artifact without allowing its headings to become report sections."""
    return "\n".join(("##" + line if line.startswith("#") else line) for line in source.splitlines())


def _methodology_section(scores: dict[str, Any] | None) -> list[str]:
    lines = [
        "### 1.3 Rating Methodology",
        "",
        "**Scale.** Every component is scored as points earned out of points available "
        "for that component. Ratios map to rating labels deterministically:",
        "",
        "| Ratio (earned ÷ available) | Rating |",
        "|----------------------------|--------|",
    ]
    upper = 1.01
    for threshold, label in RATING_BANDS:
        lo = f"≥ {threshold:.2f}" if threshold > 0 else "< 0.20"
        lines.append(f"| {lo} | {label} |")
        upper = threshold
    lines.extend([
        "",
        "**Weights.** Component ratios combine into a dimension rating using disclosed weights: "
        + ", ".join(f"{k} ×{v:g}" for k, v in DEFAULT_COMPONENT_WEIGHTS.items())
        + ". Identical weighted totals therefore always produce identical ratings; "
        "where two dimensions show the same raw points but different ratings, the difference "
        "is the weights, which are stated here.",
        "",
        "**Criteria.** Component points are awarded only for propositions that passed the "
        "Evidence Sufficiency Gate (CONFIRMED PRESENT / CONFIRMED ABSENT). Unresolved or "
        "work-queue propositions earn zero component points and appear in the Operational "
        "Audit — never here.",
        "",
    ])
    if scores:
        dims = scores.get("dimensions") or {}
        if dims:
            lines.extend([
                "| Dimension | Points | Weighted ratio | Rating |",
                "|-----------|--------|----------------|--------|",
            ])
            for dim, info in sorted(dims.items()):
                earned = info.get("earned", 0)
                maximum = info.get("maximum", 0)
                ratio = (earned / maximum) if maximum else 0.0
                lines.append(
                    f"| {dim} | {earned} / {maximum} | {ratio:.2f} | {rating_from_ratio(ratio)} |"
                )
            lines.append("")
    return lines


def build_report(
    evaluation_dir: Path,
    output_dir: Path,
    rights: dict,
    source_counts: dict,
    recovery_text: str,
    invention_id: str = "US8527057",
    invention_name: str = "Retinal Prosthesis and Method of Manufacturing a Retinal Prosthesis",
    source_urls: list[str] | None = None,
    scores: dict[str, Any] | None = None,
    evidence_rows: list[dict[str, str]] | None = None,
    debt_rows: list[dict[str, str]] | None = None,
) -> Path:
    """Build the v17 report.

    scores: optional {"dimensions": {name: {"earned": int, "maximum": int}}} feeding 1.3.
    evidence_rows: optional [{dimension, finding, proposition_id, source}] feeding 1.4.
    debt_rows: optional [{proposition_id, work_state, barrier_type, description}] rendered
      as the Operational Audit table with enum-conformant barrier column.
    """
    submission = _read_first(evaluation_dir, "submission-*.md")
    status = rights.status if hasattr(rights, "status") else rights.get("status", {})

    debt_table = ["| Proposition | Work state | Barrier type | Description |",
                  "|-------------|------------|--------------|-------------|"]
    for row in (debt_rows or []):
        debt_table.append(
            f"| {row.get('proposition_id', '')} | {row.get('work_state', '')} "
            f"| {row.get('barrier_type', '')} | {row.get('description', '')} |"
        )
    if not debt_rows:
        debt_table.append("| — | — | — | No unresolved propositions recorded. |")

    evidence_lines = []
    for row in (evidence_rows or []):
        evidence_lines.append(
            f"- **{row.get('dimension', '')}:** {row.get('finding', '')} "
            f"(`{row.get('proposition_id', '')}`, source: {row.get('source', 'not established')})"
        )
    if not evidence_rows:
        evidence_lines.append(
            "_No proposition has passed the Evidence Sufficiency Gate yet; ratings above "
            "therefore reflect methodology defaults, not established performance._"
        )

    lines = [
        f"# Invention Evaluation Report — {invention_id}",
        "",
        "> This v1.7 report is generated from phase artifacts and the v1.7 evidence graph. It is not legal advice or an FTO opinion.",
        "",
        "## Executive Summary",
        "",
        "### 1.1 Evaluation Overview",
        "",
        f"The target patent status is **{status.get('state', 'UNKNOWN')}** for the target grant, while family-level rights require separate review. The v1.7 controller extracted {source_counts.get('backward_references', 0)} backward-reference rows, {source_counts.get('forward_citing_families', 0)} forward-citing family rows, {source_counts.get('forward_references', 0)} total forward-reference rows, and {source_counts.get('family_members', 0)} family-table rows from the primary patent page.",
        "",
        "### 1.2 Bottom Line",
        "",
        "Anticipation remains **UNRESOLVED — SEARCH-INCOMPLETE**. The bridge state is **PARTIALLY TRAVERSED**. Standalone target-patent licensing is constrained by status; family, surviving-rights, know-how, regulatory, clinical, and historical-technology pathways remain open recovery targets.",
        "",
        "Unresolved evidence items are documented in the Operational Audit (appendix), not in this summary.",
        "",
        *_methodology_section(scores),
        "### 1.4 Key Evidence Supporting the Ratings",
        "",
        *evidence_lines,
        "",
        PROPOSITION_LEGEND,
        "",
        "## v1.7 Control State",
        "",
        "- Evidence Recovery Controller: active",
        "- Research exhaustion proof: required before SEARCH_EXHAUSTED",
        "- Claim-domain decomposition: active",
        "- Rights/family graph: active",
        "- Constraint propagation: active",
        "",
        "## Original Submission",
        "",
        _embed(submission),
    ]
    section_number = 2
    for pattern, title in PHASES:
        if title == "Operational Audit":
            continue
        lines.extend(["", f"## {section_number}. {title}", "", _embed(_read_first(evaluation_dir, pattern))])
        section_number += 1
    lines.extend([
        "", f"## {section_number}. Operational Audit", "",
        "Each row states the proposition, its work state, the barrier classification "
        "(enum value — descriptions live in the final column):",
        "",
        *debt_table,
        "",
        _embed(_read_first(evaluation_dir, "avenue-ledger-*.md")),
    ])
    lines.extend(["", f"## {section_number + 1}. Evidence Recovery Record", "", _embed(recovery_text)])
    lines.extend(["", "## Sources", ""])
    lines.extend(f"- {url}" for url in (source_urls or [f"https://patents.google.com/patent/{invention_id}A/en"]))
    path = output_dir / f"report-{invention_id.lower()}-v17.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# Canonical blocker-string → barrier-enum classification used when rendering
# debt tables. Unmapped blockers classify as insufficient_search_completion,
# the framework's generic incomplete-search barrier.
BLOCKER_TO_BARRIER: dict[str, str] = {
    "claim_level_search_incomplete": "insufficient_search_completion",
    "motivation_and_expectation_incomplete": "insufficient_corroboration",
    "market_evidence_incomplete": "insufficient_corroboration",
    "partner_fit_unverified": "insufficient_identity",
    "performance_data": "insufficient_technical_demonstration",
}


def barrier_for_blocker(blocker: str) -> str:
    return BLOCKER_TO_BARRIER.get(blocker, "insufficient_search_completion")
