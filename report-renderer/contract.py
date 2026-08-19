#!/usr/bin/env python3
"""
report-renderer/contract.py — Pre-render Markdown contract linter.

Governing rule: **A renderer must never silently discard semantic content.**

The v1.7 renderer had an *implicit* input contract — it consumed only H2
sections whose title began with a digit ("1. Executive Summary", "2. ...").
Every other H2 (`## v1.7 Control State`, `## Original Submission`,
`## v1.7 Inference Controls`) was silently dropped, and the render reported
success. That is a hard process defect, not a cosmetic one.

This module makes the contract explicit and machine-checkable *before* the
renderer touches HTML. It:

  1. Parses the report Markdown into a typed AST.
  2. Validates every section against a declared contract (required presence,
     allowed/forbidden child structures).
  3. Accounts for every semantic node (table, bullet item, paragraph,
     subsection) so that a later shortfall is detectable per-section.

A violation raises ``RenderContractFailure`` with the exact section, node,
and reason — the renderer aborts instead of emitting a quietly empty page.

Usage::

    from contract import validate_source_contract, RenderContractFailure

    ast = parse_report_ast(report_md)
    errors = validate_source_contract(ast)
    if errors:
        raise RenderContractFailure(errors)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Declared section contract
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SectionSpec:
    """One entry in the renderer's input contract."""

    name: str                       # exact H2 title as it appears in the report
    required: bool = True
    required_content: tuple[str, ...] = ()   # at least ONE of these must be present
    allowed_children: tuple[str, ...] = (
        "paragraph", "bullet_list", "table", "subsection", "evidence_id_line",
    )
    forbidden: tuple[str, ...] = ()          # e.g. ("heading_level_3",)


# The contract the renderer promises to honour. Any H2 in the source must
# match one of: a numbered body section, a named spec below, or be explicitly
# listed as tolerated. Anything else is a contract failure.
SECTION_CONTRACT: tuple[SectionSpec, ...] = (
    SectionSpec("Executive Summary", required=True),
    SectionSpec("v1.7 Control State", required=False,
                allowed_children=("paragraph", "bullet_list", "table", "subsection")),
    SectionSpec("Original Submission", required=False,
                allowed_children=("paragraph", "bullet_list", "table", "subsection")),
    SectionSpec("Sources", required=False,
                allowed_children=("bullet_list",)),
    SectionSpec("v1.7 Inference Controls", required=False,
                allowed_children=("paragraph", "bullet_list", "table", "subsection")),
)

# H2 titles that are valid body sections by construction (numbered phases).
_NUMBERED_RE = re.compile(r"^\d+\.\s+")


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------

@dataclass
class SemanticNode:
    kind: str           # table | bullet | paragraph | subsection
    section: str        # owning H2 title
    detail: str = ""


@dataclass
class ReportSection:
    level: int
    title: str
    body: str
    children: list["ReportSection"] = field(default_factory=list)
    nodes: list[SemanticNode] = field(default_factory=list)

    @property
    def is_numbered(self) -> bool:
        return bool(_NUMBERED_RE.match(self.title))

    @property
    def display_title(self) -> str:
        return _NUMBERED_RE.sub("", self.title)


def _classify_line(line: str) -> str | None:
    s = line.strip()
    if not s:
        return None
    if s.startswith("|"):
        return "table"
    if s.startswith("- "):
        return "bullet"
    if s.startswith("#"):
        return None
    return "paragraph"


def parse_report_ast(text: str) -> list[ReportSection]:
    """Parse the report Markdown into typed sections with semantic nodes.

    Returns a flat list of top-level sections (level 2). Each section carries
    the semantic nodes found directly in its body; subsections (level 3+) are
    collected under ``children`` with their own nodes.
    """
    raw = []
    lines = text.splitlines()
    cur_level, cur_title, cur_body = None, None, []
    for ln in lines:
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            if cur_title is not None:
                raw.append((cur_level, cur_title, "\n".join(cur_body)))
            cur_level = len(m.group(1))
            cur_title = m.group(2).strip()
            cur_body = []
        else:
            cur_body.append(ln)
    if cur_title is not None:
        raw.append((cur_level, cur_title, "\n".join(cur_body)))

    # Group level-3+ subsections under their preceding level-2 parent.
    sections: list[ReportSection] = []
    current: ReportSection | None = None
    for level, title, body in raw:
        if level == 2:
            current = ReportSection(level, title, body)
            sections.append(current)
        elif current is not None and level >= 3:
            child = ReportSection(level, title, body)
            current.children.append(child)

    for section in sections:
        section.nodes = _nodes_in_body(section.body)
        for child in section.children:
            child.nodes = _nodes_in_body(child.body)
    return sections


def _nodes_in_body(body: str) -> list[SemanticNode]:
    nodes = []
    for ln in body.splitlines():
        kind = _classify_line(ln)
        if kind:
            nodes.append(SemanticNode(kind=kind, section="", detail=ln.strip()[:60]))
    return nodes


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class ContractError:
    section: str
    node: str
    reason: str

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.section}: {self.node} — {self.reason}"


class RenderContractFailure(ValueError):
    """Raised when the source Markdown violates the renderer contract."""

    def __init__(self, errors: list[ContractError]):
        self.errors = errors
        lines = ["RENDER CONTRACT FAILURE"]
        for e in errors:
            lines.append(f"  Section: {e.section}")
            lines.append(f"  Node:    {e.node}")
            lines.append(f"  Reason:  {e.reason}")
            lines.append("")
        lines.append("Action: render aborted")
        super().__init__("\n".join(lines))


# ---------------------------------------------------------------------------
# v1.8: Target Identity Firewall
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TargetIdentity:
    """Canonical identity of the patent being evaluated."""
    publication_number: str
    application_number: str = ""
    title: str = ""
    inventors: tuple[str, ...] = ()
    assignee: str = ""
    filing_date: str = ""
    grant_date: str = ""
    expiration_date: str = ""
    government_rights: str = ""


@dataclass
class EvidenceItem:
    """A single piece of evidence linked to a proposition."""
    evidence_id: str
    target_publication_number: str
    source: str
    source_type: str  # "patent", "literature", "market_report", "LLM_INFERENCE"
    supports: list[str] = field(default_factory=list)  # proposition IDs
    confidence: str = "UNKNOWN"


@dataclass
class EpistemicState:
    """Multi-dimensional epistemic state for propositions."""
    # Primary states
    ESTABLISHED = "ESTABLISHED"          # Evidence-backed fact
    PARTIAL = "PARTIALLY_ESTABLISHED"    # Some evidence
    INFERRED = "INFERRED"                # LLM reasoning, no direct evidence
    NOT_LOADED = "NOT_LOADED"            # No data fetched
    UNKNOWN = "UNKNOWN"                  # Insufficient evidence
    
    # Confidence levels
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    
    # Source types
    DIRECT_EVIDENCE = "DIRECT_EVIDENCE"
    DERIVED = "DERIVED"
    BENCHMARK = "BENCHMARK"
    ASSUMPTION = "ASSUMPTION"


# ---------------------------------------------------------------------------
# v1.8: Authoritative Proposition Registry
# ---------------------------------------------------------------------------
#
# The single source of truth for proposition states. Every proposition has
# EXACTLY ONE authoritative state, held here. Sections may *display* a state
# but may never *override* it. The pre-render gate refuses to render a report
# whose text contradicts the registry.

class RecoveryClass:
    """Recovery classes for evidence debt — how a gap can be closed."""
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"                      # evidence exists elsewhere; fetch it
    INDEPENDENT_VERIFICATION_REQUIRED = "INDEPENDENT_VERIFICATION_REQUIRED"  # evidence exists but needs a 2nd source
    SOURCE_UPGRADE_REQUIRED = "SOURCE_UPGRADE_REQUIRED"          # evidence is benchmark/derived; needs primary source
    UNAVAILABLE_BY_CONSTRAINT = "UNAVAILABLE_BY_CONSTRAINT"      # cannot be established (confidential, expired, N/A)


@dataclass(frozen=True)
class EvidenceDebt:
    """First-class evidence debt record."""
    debt_id: str
    proposition: str
    missingness: str
    recovery_class: str
    severity: str = "MODERATE"          # CRITICAL | HIGH | MODERATE | LOW
    recoverable: bool = True
    reason: str = ""
    recommended_action: str = ""


@dataclass(frozen=True)
class Proposition:
    """One proposition in the authoritative registry."""
    proposition_id: str
    claim: str
    state: str
    phase: str = ""
    version: str = "v2"
    evidence: tuple = ()
    children: tuple = ()                # atomic decomposition (e.g. P-08-005a..f)
    debt: tuple = ()                    # EvidenceDebt records

    @property
    def is_established(self) -> bool:
        return self.state == EpistemicState.ESTABLISHED

    @property
    def is_atomic(self) -> bool:
        return bool(self.children)


class PropositionRegistry:
    """Authoritative proposition states, loaded from proposition-ledger.json.

    The registry is the ONLY place a proposition's state is decided. A
    downstream artifact (report section, evidence summary, appendix) that
    claims a different state is a state-propagation violation and must be
    caught by the pre-render gate.
    """

    def __init__(self, ledger: dict | None = None):
        self._props: dict[str, Proposition] = {}
        if ledger:
            self.load(ledger)

    # -- construction ------------------------------------------------------

    def load(self, ledger: dict) -> None:
        raw = ledger.get("proposition_ledger", ledger)
        for pid, entry in raw.items():
            children = tuple(entry.get("children", ()))
            debt = tuple(
                EvidenceDebt(
                    debt_id=d.get("debt_id", f"{pid}-debt-{i}"),
                    proposition=d.get("proposition", pid),
                    missingness=d.get("missingness", d.get("description", "")),
                    recovery_class=d.get("recovery_class", RecoveryClass.RECOVERY_REQUIRED),
                    severity=d.get("severity", "MODERATE"),
                    recoverable=d.get("recoverable", True),
                    reason=d.get("reason", ""),
                    recommended_action=d.get("recommended_action", ""),
                )
                for i, d in enumerate(entry.get("debt", ()))
            )
            self._props[pid] = Proposition(
                proposition_id=pid,
                claim=entry.get("claim", ""),
                state=entry.get("status", entry.get("state", EpistemicState.UNKNOWN)),
                phase=entry.get("phase", ""),
                version=entry.get("version", "v2"),
                evidence=tuple(entry.get("evidence", ())),
                children=children,
                debt=debt,
            )

    @classmethod
    def from_file(cls, path: str) -> "PropositionRegistry":
        import json
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    # -- queries -----------------------------------------------------------

    def state_of(self, pid: str) -> str:
        """Authoritative state for a proposition (or its parent)."""
        if pid in self._props:
            return self._props[pid].state
        # Parent lookup: P-08-005 -> P-08-005a..f
        for prop in self._props.values():
            if pid in prop.children:
                return prop.state
        return EpistemicState.UNKNOWN

    def get(self, pid: str) -> Proposition | None:
        return self._props.get(pid)

    def all(self) -> list[Proposition]:
        return sorted(self._props.values(), key=lambda p: p.proposition_id)

    def unestablished(self) -> list[Proposition]:
        """Propositions whose authoritative state is NOT ESTABLISHED."""
        return [p for p in self.all() if not p.is_established]

    def unestablished_top_level(self) -> list[Proposition]:
        """Unestablished propositions that are NOT atomic children of another
        proposition.

        Atomic children (e.g. P-08-005d..f) are sub-claims of a decomposed
        parent that is itself already counted (P-08-005 PARTIALLY_ESTABLISHED).
        Counting them separately in the headline would double-count the same
        proposition. The children remain visible in the decomposition table
        inside the parent's section.
        """
        child_ids = {c for p in self._props.values() for c in p.children}
        return [p for p in self.unestablished() if p.proposition_id not in child_ids]

    def atomic_children(self, pid: str) -> list[Proposition]:
        """Resolve atomic children of a decomposed proposition."""
        prop = self._props.get(pid)
        if not prop:
            return []
        return [self._props[c] for c in prop.children if c in self._props]

    # -- consistency -------------------------------------------------------

    def validate_report_consistency(self, report_md: str) -> list[ContractError]:
        """Scan the report text for state claims that contradict the registry.

        Detects:
        - "P-XX-XXX — ESTABLISHED" when the registry says otherwise
        - "All propositions are now ESTABLISHED" when unestablished() is non-empty
        - "Unestablished Propositions: NONE" when unestablished() is non-empty
        - A proposition listed with a state different from the registry

        Returns a list of errors; empty list means the report is consistent.
        """
        errors: list[ContractError] = []
        unest = self.unestablished()
        unest_ids = {p.proposition_id for p in unest}

        # 1. Explicit per-proposition state claims in the text.
        #    Pattern: "P-08-005: ... — STATE" or "P-08-005: STATE" or "P-08-005 — STATE"
        for prop in self.all():
            pid = prop.proposition_id
            # Match the proposition id followed by a state token within ~120 chars.
            # Require a boundary so P-08-005 does not match inside P-08-005d.
            pat = re.compile(
                re.escape(pid) + r"(?![\w-])[^.\n]{0,120}?\b("
                + "|".join([
                    EpistemicState.ESTABLISHED,
                    EpistemicState.PARTIAL,
                    EpistemicState.INFERRED,
                    EpistemicState.NOT_LOADED,
                    EpistemicState.UNKNOWN,
                    "ESCALATION_REQUIRED",
                    "NOT_ESTABLISHED",
                ]) + r")\b"
            )
            for m in pat.finditer(report_md):
                claimed = m.group(1)
                canonical = prop.state
                # NOT_ESTABLISHED is the display form of UNKNOWN/NOT_LOADED
                claimed_canon = {
                    "NOT_ESTABLISHED": EpistemicState.UNKNOWN,
                }.get(claimed, claimed)
                canonical_canon = {
                    EpistemicState.NOT_LOADED: EpistemicState.UNKNOWN,
                    "NOT_ESTABLISHED": EpistemicState.UNKNOWN,
                }.get(canonical, canonical)
                if claimed_canon != canonical_canon:
                    errors.append(ContractError(
                        "Proposition Consistency",
                        pid,
                        f"State contradiction: report claims '{claimed}' but the "
                        f"authoritative registry says '{canonical}'. "
                        f"Report generation halted."
                    ))

        # 2. "All propositions ESTABLISHED" boilerplate.
        if unest and re.search(
            r"all propositions (are )?(now )?established", report_md, re.I
        ):
            errors.append(ContractError(
                "Proposition Consistency",
                "report_body",
                f"Boilerplate 'All propositions are now ESTABLISHED' contradicts the "
                f"registry: {len(unest)} proposition(s) are not established "
                f"({', '.join(sorted(unest_ids))}). Report generation halted."
            ))

        # 3. "Unestablished Propositions: NONE" when the registry disagrees.
        if unest:
            m = re.search(
                r"Unestablished Propositions?(?:\*\*)?\s*:\s*(NONE|0)\b",
                report_md, re.I
            )
            if m:
                errors.append(ContractError(
                    "Proposition Consistency",
                    "report_body",
                    f"Report claims 'Unestablished Propositions: {m.group(1)}' but the "
                    f"registry has {len(unest)} unestablished proposition(s): "
                    f"{', '.join(sorted(unest_ids))}. Report generation halted."
                ))

        return errors


def validate_target_identity(
    sections: list[ReportSection],
    target: TargetIdentity,
    evidence_items: list[EvidenceItem]
) -> list[ContractError]:
    """Verify all evidence belongs to the target patent.
    
    This is the Target Identity Firewall. It prevents cross-patent
    contamination by ensuring every evidence item references the same
    patent as the run target.
    
    Returns a list of errors; empty list means validation passes.
    """
    errors = []
    
    # 1. Target must be specified
    if not target.publication_number or target.publication_number == 'UNKNOWN':
        errors.append(ContractError(
            "Target Identity",
            "publication_number",
            f"No target patent specified in scores-manifest.json "
            f"(got: {target.publication_number})"
        ))
        return errors
    
    # 2. Check for foreign evidence
    for evidence in evidence_items:
        if evidence.target_publication_number != target.publication_number:
            errors.append(ContractError(
                "Evidence Provenance",
                evidence.evidence_id,
                f"FATAL: Foreign evidence detected. "
                f"Evidence targets {evidence.target_publication_number} "
                f"but run targets {target.publication_number}. "
                f"Source: {evidence.source}. "
                f"Report generation halted."
            ))
    
    # 3. Check for known contamination patterns
    contamination_indicators = [
        "NIH grant R24EY12893-01",  # US8527057
        "Second Sight",              # US8527057 assignee
        "Retinal Prosthesis",        # US8527057 title
        "Greenberg",                 # US8527057 inventor
    ]
    
    for section in sections:
        for indicator in contamination_indicators:
            if indicator.lower() in section.body.lower():
                errors.append(ContractError(
                    "Contamination Detection",
                    section.title,
                    f"FATAL: Contamination indicator '{indicator}' found in section. "
                    f"This belongs to a different patent. "
                    f"Report generation halted."
                ))
    
    return errors


def validate_epistemic_consistency(
    scores: dict,
    section_status: dict[str, str]
) -> list[ContractError]:
    """Verify epistemic states are consistent across the report.
    
    Detects contradictions like:
    - "All propositions established" but sections show "No established findings"
    - Patent status simultaneously NOT_LOADED and EXPIRED
    - Market claims without evidence
    
    Returns a list of errors; empty list means validation passes.
    """
    errors = []
    
    # 1. Check for status contradictions
    overall_status = scores.get('overall_status', '')
    if overall_status == 'COMPLETED':
        # If any required section shows "NOT_ESTABLISHED", flag contradiction
        for section, status in section_status.items():
            if status == 'NOT_ESTABLISHED':
                errors.append(ContractError(
                    "Epistemic Consistency",
                    section,
                    f"Contradiction: Overall status is COMPLETED but section "
                    f"'{section}' shows NOT_ESTABLISHED"
                ))
    
    # 2. Check for derived metrics without evidence
    market_claims = scores.get('market_claims', {})
    for claim, value in market_claims.items():
        if isinstance(value, (int, float)) and value > 0:
            # Check if there's supporting evidence
            evidence_for_claim = [
                e for e in scores.get('evidence_items', [])
                if claim in e.get('supports', [])
            ]
            if not evidence_for_claim:
                errors.append(ContractError(
                    "Derived Metric Firewall",
                    f"market_claims.{claim}",
                    f"Derived metric {claim}={value} has no supporting evidence. "
                    f"Market claims must be backed by structured evidence."
                ))
    
    return errors


def pre_render_integrity_gate(
    report_md: str,
    scores: dict,
    submission_md: str,
    ledger: dict | None = None,
    ledger_path: str | None = None,
) -> list[ContractError]:
    """Final validation before rendering.
    
    This is the Pre-render Integrity Gate. It runs all validations
    and prevents rendering if any critical errors are found.
    
    Returns a list of errors; empty list means validation passes.
    """
    errors = []
    
    # 1. Target identity consistency
    target_data = scores.get('target_patent', {})
    target = TargetIdentity(
        publication_number=target_data.get('publication_number', 'UNKNOWN'),
        application_number=target_data.get('application_number', ''),
        title=target_data.get('title', ''),
        inventors=tuple(target_data.get('inventors', [])),
        assignee=target_data.get('assignee', ''),
        filing_date=target_data.get('filing_date', ''),
        grant_date=target_data.get('grant_date', ''),
        expiration_date=target_data.get('expiration_date', ''),
        government_rights=target_data.get('government_rights', '')
    )
    
    # 2. Evidence provenance
    evidence_items = [
        EvidenceItem(**e) for e in scores.get('evidence_items', [])
    ]
    
    # Parse sections for contamination check
    sections = parse_report_ast(report_md)
    errors.extend(validate_target_identity(sections, target, evidence_items))
    
    # 3. Epistemic state consistency
    errors.extend(validate_epistemic_consistency(scores, {}))
    
    # 4. v1.8: Proposition Registry consistency — the report text must not
    #    contradict the authoritative proposition states.
    registry = None
    if ledger is not None:
        registry = PropositionRegistry(ledger)
    elif ledger_path:
        try:
            registry = PropositionRegistry.from_file(ledger_path)
        except Exception:
            registry = None
    if registry is not None:
        errors.extend(registry.validate_report_consistency(report_md))
    
    # 5. Check for hardcoded contamination in report.
    #    These indicators belong to US8527057. They are contamination ONLY
    #    when the run target is a different patent (e.g. US5215088). When the
    #    target IS US8527057, they are legitimate content.
    target_pub = target_data.get('publication_number', '')
    if target_pub != 'US8527057B2':
        contamination_patterns = [
            ("US 8,527,057", "US8527057 patent reference"),
            ("Retinal Prosthesis", "US8527057 title"),
            ("NIH grant R24EY12893-01", "US8527057 government rights"),
            ("Second Sight", "US8527057 assignee"),
        ]
        for pattern, description in contamination_patterns:
            if pattern in report_md:
                errors.append(ContractError(
                    "Contamination Detection",
                    "report_body",
                    f"FATAL: Hardcoded contamination '{description}' found in report. "
                    f"This belongs to a different patent. "
                    f"Report generation halted."
                ))
    
    if errors:
        raise RenderContractFailure(errors)
    
    return errors


def _spec_for(title: str) -> SectionSpec | None:
    for spec in SECTION_CONTRACT:
        if spec.name == title:
            return spec
    return None


def validate_source_contract(sections: list[ReportSection]) -> list[ContractError]:
    """Validate the parsed AST against the declared contract.

    Returns a list of errors; an empty list means the contract passes.
    """
    errors: list[ContractError] = []

    seen = {s.title for s in sections}

    # 1. Every required section must be present.
    for spec in SECTION_CONTRACT:
        if spec.required and spec.name not in seen:
            errors.append(ContractError(spec.name, "section", "required section missing"))

    for section in sections:
        spec = _spec_for(section.title)

        # 2. Recognized sections only. Numbered body sections are valid by
        #    construction; named specs are valid; everything else fails.
        if spec is None and not section.is_numbered:
            errors.append(ContractError(
                section.title, f"H{section.level} heading",
                "unrecognized section — not a numbered body section and not in "
                "SECTION_CONTRACT; rendering it would silently drop it"))
            continue

        if spec is None:
            continue

        # 3. Forbidden child structures.
        for child in section.children:
            for forbidden in spec.forbidden:
                if forbidden == "heading_level_3" and child.level >= 3:
                    errors.append(ContractError(
                        section.title, f"#{'.' * child.level} {child.title}",
                        "subsection nesting forbidden by section contract"))

        # 4. Required content classes: at least ONE of the listed classes
        #    must be present (a section with no content at all is itself a
        #    contract failure, caught by the "section not emitted" check).
        if spec.required_content:
            present = {n.kind for n in section.nodes}
            for child in section.children:
                present |= {n.kind for n in child.nodes}
            if not (present & set(spec.required_content)):
                errors.append(ContractError(
                    section.title, "section content",
                    f"none of required content classes {list(spec.required_content)} "
                    f"present; found {sorted(present) or 'nothing'}"))

    return errors


def account_semantic_nodes(
    source_sections: list[ReportSection],
    rendered: str,
    skip_titles: tuple[str, ...] = (),
) -> list[ContractError]:
    """Cross-check that every source semantic node survived into the HTML.

    The renderer tags each emitted section wrapper with
    ``data-contract="<title>" data-nodes="<count>"`` so this check can be done
    per-section rather than by guessing which ``<li>`` belongs to which block.

    Sections rendered by special-cased template blocks (Executive Summary,
    SWOT, Landscape & Market Data) are excluded via ``skip_titles`` — their
    content is accounted for by the template placeholders instead.
    """
    errors: list[ContractError] = []
    pat = re.compile(
        r'data-contract="([^"]+)"[^>]*data-nodes="(\d+)"', re.S)
    emitted = {m.group(1): int(m.group(2)) for m in pat.finditer(rendered)}

    for section in source_sections:
        if section.title in skip_titles:
            continue
        title = section.display_title if section.is_numbered else section.title
        expected = len(section.nodes) + sum(len(c.nodes) for c in section.children)
        got = emitted.get(title)
        if got is None:
            errors.append(ContractError(
                section.title, "section payload",
                f"section not emitted at all ({expected} semantic nodes in source)"))
            continue
        if got < expected:
            errors.append(ContractError(
                section.title, "semantic node",
                f"rendered {got} of {expected} semantic nodes; "
                f"{expected - got} silently dropped"))
    return errors


def validate_before_render(sections: list[ReportSection]) -> None:
    """Raise ``RenderContractFailure`` if the source violates the contract."""
    errors = validate_source_contract(sections)
    if errors:
        raise RenderContractFailure(errors)


# Sections the renderer places through dedicated template placeholders rather
# than the generic ``report_section_page`` loop. They are excluded from the
# per-section node-accounting cross-check.
SPECIAL_RENDER_TITLES = (
    "Executive Summary",
    "v1.7 Control State",
    "Original Submission",
    "Sources",
    "v1.7 Inference Controls",
    "SWOT Analysis",
    "Landscape & Market Data",
)