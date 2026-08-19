"""Renderer contract + integrity tests.

These tests exist to catch the failure mode the v1.7 renderer had: a valid
Markdown report rendered to an "apparently successful" PDF while substantive
content (claim mappings, literature, partners, feature-benefit material)
vanished because the renderer's body loop only consumed *numbered* H2
sections.

Two independent assertions per test:

  1. **Contract validation** — a fixture containing every supported content
     type passes; a fixture with unsupported structures raises
     ``RenderContractFailure`` with the exact offending node.
  2. **Node accounting** — after rendering, every semantic node in the source
     AST must be accounted for in the output. A shortfall means content was
     silently dropped, and the render must fail.

The deliberately-bad fixture ("garbage_section") is the negative control: it
must be *rejected*, never silently skipped.
"""

import importlib.util
import re
from pathlib import Path

import pytest

from contract import (
    ReportSection,
    SemanticNode,
    SECTION_CONTRACT,
    account_semantic_nodes,
    parse_report_ast,
    validate_source_contract,
    validate_before_render,
    RenderContractFailure,
)


def _renderer_module():
    path = Path(__file__).parents[2] / "report-renderer" / "render_report.py"
    spec = importlib.util.spec_from_file_location("render_report_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GOOD_REPORT = """\
# Good Report

## Executive Summary

- Finding one.
- Finding two.

## 1. Established Findings

| proposition_id | Finding | Source |
|---|---|---|
| P-01-001 | first row | Google Patents |

### 1.1 Submission and chronology

| proposition_id | Finding | Source identity |
|---|---|---|
| P-02-001 | filed 1890-03-26 | Patent header |

### 1.2 Technology profile

- bullet under a subsection
- second bullet

## 2. Analytical Conclusions

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-05-009 | NOT ANTICIPATED | P-05-002 | Anticipation gate |

**Reasoning:** Every identified reference misses at least one Claim 1 limitation.

## 3. Operational Audit

| proposition_id | Proposition | Barrier type | Avenue summary |
|---|---|---|---|
| P-02-004 | No public disclosure | insufficient_search_completion | A1 COMPLETE |

## 4. Report constraints verification

| Constraint | Status |
|---|---|
| Executive Summary subset | PASS |

## v1.7 Control State

- Evidence Recovery Controller: active
- Claim-domain decomposition: active

## Sources

- https://patents.google.com/patent/US433700A
- https://www.uspto.gov/
"""


BAD_REPORT = """\
# Bad Report

## Executive Summary

- Finding one.

## 1. Established Findings

| proposition_id | Finding | Source |
|---|---|---|
| P-01-001 | first row | Google Patents |

## This section is not in the contract and not numbered

- content that would be silently dropped by the old renderer
"""


# ---------------------------------------------------------------------------
# Contract validation
# ---------------------------------------------------------------------------

def test_good_report_passes_source_contract():
    ast = parse_report_ast(GOOD_REPORT)
    errors = validate_source_contract(ast)
    assert errors == [], f"unexpected contract errors: {errors}"


def test_unrecognized_section_is_rejected_not_silently_dropped():
    ast = parse_report_ast(BAD_REPORT)
    errors = validate_source_contract(ast)
    assert errors, "expected a contract failure for the unrecognized section"
    messages = " ".join(str(e) for e in errors)
    assert "This section is not in the contract" in messages
    assert "silently drop" in messages


def test_validate_before_render_raises_on_bad_source():
    ast = parse_report_ast(BAD_REPORT)
    with pytest.raises(RenderContractFailure) as exc_info:
        validate_before_render(ast)
    assert "This section is not in the contract" in str(exc_info.value)


def test_required_section_missing_is_rejected():
    report = GOOD_REPORT.replace("## Executive Summary", "## Executive Summary\n\nplaceholder")
    # Remove the Executive Summary heading entirely to simulate a missing one.
    report = re.sub(r"## Executive Summary\n", "", GOOD_REPORT, count=1)
    ast = parse_report_ast(report)
    errors = validate_source_contract(ast)
    assert any("required section missing" in str(e) and "Executive Summary" in str(e)
               for e in errors), errors


# ---------------------------------------------------------------------------
# Node accounting (the "zero semantic nodes disappear" invariant)
# ---------------------------------------------------------------------------

def test_every_semantic_node_survives_render():
    renderer = _renderer_module()
    ast = parse_report_ast(GOOD_REPORT)
    # Minimal scores manifest so render() can run.
    scores = {
        "run_id": "RUN-integrity",
        "invention_name": "Integrity Fixture",
        "submitted_by": "Tester",
        "invention_id": "US433700",
        "submitted_date": "2026-08-16",
        "report_date": "2026-08-16",
        "disclaimer": "Not legal advice.",
        "gauges": {},
        "charts": {},
        "swot": {},
        "target_patent": {
            "publication_number": "US433700A",
            "title": "Integrity Fixture",
        },
        "evidence_items": [],
    }
    html = renderer.render(GOOD_REPORT, "", scores)
    from contract import SPECIAL_RENDER_TITLES
    errors = account_semantic_nodes(ast, html, skip_titles=SPECIAL_RENDER_TITLES)
    assert errors == [], f"semantic nodes were dropped: {errors}"


def test_render_aborts_when_content_would_be_lost():
    """The renderer must refuse to emit HTML when a source section is not
    represented in the output — this is the regression guard for the v1.7
    silent-drop bug."""
    renderer = _renderer_module()
    ast = parse_report_ast(BAD_REPORT)
    scores = {
        "run_id": "RUN-integrity", "invention_name": "Bad", "submitted_by": "T",
        "invention_id": "US000", "submitted_date": "2026-08-16",
        "report_date": "2026-08-16", "disclaimer": "x", "gauges": {},
        "charts": {}, "swot": {},
    }
    with pytest.raises(RenderContractFailure):
        renderer.render(BAD_REPORT, "", scores)


def test_node_accounting_flags_partial_loss():
    """If a section emits fewer nodes than the source contains, the
    accounting check must name the exact section and the shortfall."""
    ast = parse_report_ast(GOOD_REPORT)
    # Simulate a renderer that dropped one bullet from "Sources".
    fake_html = (
        '<div class="page" data-contract="Executive Summary" data-nodes="2">'
        '<h2 class="sec">Executive Summary</h2></div>'
        '<div class="page" data-contract="Sources" data-nodes="1">'
        '<h2 class="sec">Sources</h2>'
        '<ul class="bullets"><li>only one</li></ul></div>'
    )
    errors = account_semantic_nodes(ast, fake_html)
    assert errors, "expected an accounting error for the shortfall"
    sources_errors = [e for e in errors if e.section == "Sources"]
    assert sources_errors, f"expected a Sources shortfall, got {[e.section for e in errors]}"
    e = sources_errors[0]
    assert "1 of 2" in e.reason or "silently dropped" in e.reason


def test_node_accounting_flags_missing_section_payload():
    ast = parse_report_ast(GOOD_REPORT)
    # No section wrapper for "v1.7 Control State" at all.
    fake_html = ""
    errors = account_semantic_nodes(ast, fake_html)
    sections_reported = {e.section for e in errors}
    assert "v1.7 Control State" in sections_reported


def test_section_spec_contract_is_machine_readable():
    """SECTION_CONTRACT must be a real, non-empty list of SectionSpecs so the
    renderer's promise is inspectable by tooling."""
    assert SECTION_CONTRACT
    for spec in SECTION_CONTRACT:
        assert spec.name
        assert isinstance(spec.required, bool)
        assert isinstance(spec.allowed_children, tuple)
        assert isinstance(spec.forbidden, tuple)


def test_parse_report_ast_attaches_subsections_to_parents():
    ast = parse_report_ast(GOOD_REPORT)
    by_title = {s.title: s for s in ast}
    assert "1. Established Findings" in by_title
    children = by_title["1. Established Findings"].children
    titles = [c.title for c in children]
    assert "1.1 Submission and chronology" in titles
    assert "1.2 Technology profile" in titles


def test_parse_report_ast_counts_subsection_nodes():
    ast = parse_report_ast(GOOD_REPORT)
    by_title = {s.title: s for s in ast}
    sec = by_title["1. Established Findings"]
    # Direct body nodes: the P-01 table (1 table node) = 1
    assert len(sec.nodes) >= 1
    # Subsection 1.2 has 2 bullets
    sub = next(c for c in sec.children if c.title == "1.2 Technology profile")
    assert len(sub.nodes) == 2


def test_supported_content_types_are_all_accounted_for():
    """Every content class the renderer can emit must be classifiable by the
    linter, otherwise a node type could fall through both checks and vanish."""
    from contract import _classify_line
    samples = {
        "| a | b |": "table",
        "- bullet item": "bullet",
        "plain paragraph text": "paragraph",
    }
    for line, expected in samples.items():
        assert _classify_line(line) == expected, line