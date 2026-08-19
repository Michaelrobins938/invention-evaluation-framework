"""Build a v1.7 report from phase artifacts and graph state, never from v1.6 PDF/MD."""

from __future__ import annotations

from pathlib import Path


PHASES = [
    ("technology-profile-*.md", "Technology Analysis"),
    ("patent-landscape-*.md", "Patent Landscape Analysis"),
    ("novelty-search-*.md", "IP / Novelty Analysis"),
    ("literature-search-*.md", "Literature Analysis"),
    ("market-analysis-*.md", "Market Analysis"),
    ("partner-analysis-*.md", "Potential Partners"),
    ("avenue-ledger-*.md", "Operational Audit"),
]


def _read_first(directory: Path, pattern: str) -> str:
    matches = sorted(directory.glob(pattern))
    return matches[0].read_text(encoding="utf-8") if matches else "_No phase artifact was produced._"


def _embed(source: str) -> str:
    """Embed a source artifact without allowing its headings to become report sections."""
    return "\n".join(("##" + line if line.startswith("#") else line) for line in source.splitlines())


def build_report(
    evaluation_dir: Path,
    output_dir: Path,
    rights: dict,
    source_counts: dict,
    recovery_text: str,
    invention_id: str = "US8527057",
    invention_name: str = "Retinal Prosthesis and Method of Manufacturing a Retinal Prosthesis",
    source_urls: list[str] | None = None,
) -> Path:
    submission = _read_first(evaluation_dir, "submission-*.md")
    status = rights.status if hasattr(rights, "status") else rights.get("status", {})
    lines = [
        f"# Invention Evaluation Report — {invention_id}",
        "",
        "> This v1.7 report is generated from phase artifacts and the v1.7 evidence graph. It is not legal advice or an FTO opinion.",
        "",
        "## Executive Summary",
        "",
        f"The target patent status is **{status.get('state', 'UNKNOWN')}** for the target grant, while family-level rights require separate review. The v1.7 controller extracted {source_counts.get('backward_references', 0)} backward-reference rows, {source_counts.get('forward_citing_families', 0)} forward-citing family rows, {source_counts.get('forward_references', 0)} total forward-reference rows, and {source_counts.get('family_members', 0)} family-table rows from the primary patent page.",
        "",
        "Anticipation remains **UNRESOLVED — SEARCH-INCOMPLETE**. The bridge state is **PARTIALLY TRAVERSED**. Standalone target-patent licensing is constrained by status; family, surviving-rights, know-how, regulatory, clinical, and historical-technology pathways remain open recovery targets.",
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
    lines.extend(["", f"## {section_number}. Operational Audit", "", _embed(_read_first(evaluation_dir, "avenue-ledger-*.md"))])
    lines.extend(["", f"## {section_number + 1}. Evidence Recovery Record", "", _embed(recovery_text)])
    lines.extend(["", "## Sources", ""])
    lines.extend(f"- {url}" for url in (source_urls or [f"https://patents.google.com/patent/{invention_id}A/en"]))
    path = output_dir / f"report-{invention_id.lower()}-v17.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
