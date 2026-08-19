"""Visual QA gate tests.

`pdftotext` answers "does text exist in the PDF?" It does **not** answer
"is the PDF visually correct?" A clipped watermark, a footer collision, an
orphan heading, or a table overflowing its page all pass a text-only check
while failing visually.

This module defines the two verification classes the pipeline requires:

  Structural QA  — PDF exists, page count, expected headings, TOC
                   destinations, proposition IDs, required tables, expected
                   text, no missing sections.
  Visual QA      — rasterize the designated critical pages and inspect for
                   clipping, overlaps, page breaks, footer collisions,
                   headers, badges, table overflow, whitespace anomalies,
                   orphan headings, and TOC alignment.

Both gates must pass before the report may be marked complete.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

RENDERER_DIR = Path(__file__).resolve().parents[1]
if str(RENDERER_DIR) not in sys.path:
    sys.path.insert(0, str(RENDERER_DIR))

from visual_qa import (  # noqa: E402
    CRITICAL_PAGES,
    VisualQAReport,
    report_to_dict,
    run_visual_qa,
    structural_checks,
    visual_checks,
)


def _renderer_module():
    path = RENDERER_DIR / "render_report.py"
    spec = importlib.util.spec_from_file_location("render_report_vqa", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SAMPLE_PDF = (
    Path(__file__).resolve().parents[2]
    / "evaluations/us8527057-v17(Complete-pass)/report-us8527057-v17.pdf"
)
# Negative control: a fixture produced by the *old* renderer, whose body loop
# only consumed numbered H2 sections and silently dropped
# ``v1.7 Control State``, ``Original Submission`` and ``v1.7 Inference
# Controls``. The visual QA gate must reject it.
BROKEN_PDF = (
    Path(__file__).resolve().parents[2]
    / "evaluations/us8527057-v17(Complete-pass)/report-us8527057-v17-broken-fixture.pdf"
)
SAMPLE_HEADINGS = (
    "Executive Summary", "v1.7 Control State", "Original Submission",
    "Technology Analysis", "Patent Landscape Analysis", "IP / Novelty Analysis",
    "Literature Analysis", "Market Analysis", "Potential Partners",
    "Operational Audit", "Evidence Recovery Record", "Sources",
    "v1.7 Inference Controls", "SWOT Analysis", "Landscape & Market Data",
)
DROPPED_HEADINGS = (
    "heading:v1.7 Control State",
    "heading:Original Submission",
    "heading:v1.7 Inference Controls",
)


def _pdf_page_count(pdf_path: str) -> int:
    """Read the physical page count from the PDF itself.

    Hard-coding a page count is wrong: the US8527057 report is 29 pages and
    the 7149534 report is 47. The gate checks that the render produced a
    complete, well-formed document of whatever length the invention requires.
    """
    import subprocess
    info = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
    for line in info.splitlines():
        if line.lower().startswith("pages:"):
            return int(line.split(":")[1].strip())
    return 0


@pytest.fixture(scope="module")
def fixed_pdf(tmp_path_factory):
    """Render the source Markdown through the fixed renderer for a positive
    control. The render is gated by the contract linter, so this fixture
    exercises the full fixed path."""
    renderer = _renderer_module()
    import json
    D = (Path(__file__).resolve().parents[2]
         / "evaluations/us8527057-v17(Complete-pass)")
    md = (D / "report-us8527057-v17.md").read_text(encoding="utf-8")
    scores = json.loads((D / "scores-us8527057-v17.json").read_text(encoding="utf-8"))
    # v1.8 integrity gate requires target identity + evidence provenance.
    scores.setdefault("target_patent", {
        "publication_number": "US8527057B2",
        "title": "Retinal Prosthesis",
        "government_rights": "NIH grant R24EY12893-01",
    })
    scores.setdefault("evidence_items", [])
    html = renderer.render(
        md, (D / "recovery-evidence-us8527057-v17.md").read_text(encoding="utf-8"),
        scores)
    out = tmp_path_factory.mktemp("fixed") / "report.html"
    out.write_text(html, encoding="utf-8")
    pdf = out.with_suffix(".pdf")
    renderer.export_pdf(str(out), str(pdf))
    return pdf


@pytest.mark.skipif(not BROKEN_PDF.exists(), reason="broken fixture not present")
def test_broken_fixture_is_rejected_by_structural_qa():
    """The broken fixture was produced by the old renderer, which silently
    dropped three sections. The structural QA gate must catch that — it is
    the regression guard."""
    pages = _pdf_page_count(BROKEN_PDF)
    report = run_visual_qa(
        str(BROKEN_PDF), expected_headings=SAMPLE_HEADINGS,
        expected_min_pages=pages)
    failed = {c.name for c in report.structural if not c.passed}
    for dropped in DROPPED_HEADINGS:
        assert dropped in failed, (
            f"{dropped} was not flagged as missing — the structural gate "
            f"would have let the silent drop through")


@pytest.mark.skipif(not BROKEN_PDF.exists(), reason="broken fixture not present")
def test_broken_fixture_fails_visual_qa():
    pages = _pdf_page_count(BROKEN_PDF)
    report = run_visual_qa(
        str(BROKEN_PDF), expected_headings=SAMPLE_HEADINGS,
        expected_min_pages=pages)
    assert not report.passed


def test_fixed_render_passes_visual_qa(fixed_pdf):
    pages = _pdf_page_count(fixed_pdf)
    report = run_visual_qa(
        str(fixed_pdf), expected_headings=SAMPLE_HEADINGS,
        expected_min_pages=pages, expected_max_pages=pages)
    assert report.passed, [
        c.detail for c in report.structural if not c.passed
    ] + [f"{c.page}: {c.issues}" for c in report.visual if not c.passed]


def test_fixed_render_rasterizes_all_critical_pages(fixed_pdf):
    pages = _pdf_page_count(fixed_pdf)
    report = run_visual_qa(
        str(fixed_pdf), expected_headings=SAMPLE_HEADINGS,
        expected_min_pages=pages, expected_max_pages=pages)
    assert len(report.rasterized_pages) == len(CRITICAL_PAGES), (
        f"expected {len(CRITICAL_PAGES)} rasterized pages, "
        f"got {len(report.rasterized_pages)}")


@pytest.mark.skipif(not BROKEN_PDF.exists(), reason="broken fixture not present")
def test_broken_fixture_rasterizes_locatable_critical_pages():
    """Every critical page that can be located in the broken fixture must be
    rasterized; pages that cannot be located are reported as failed visual
    checks rather than silently skipped."""
    pages = _pdf_page_count(BROKEN_PDF)
    report = run_visual_qa(
        str(BROKEN_PDF), expected_headings=SAMPLE_HEADINGS,
        expected_min_pages=pages, expected_max_pages=pages)
    failed_visual = {c.page for c in report.visual if not c.passed}
    for name in failed_visual:
        assert name in CRITICAL_PAGES, f"unexpected failed visual page: {name}"


def test_structural_checks_report_page_size():
    checks = structural_checks(
        "/nonexistent.pdf", expected_min_pages=1)
    # No PDF → pdfinfo returns empty; the checks fail closed.
    assert any(not c.passed for c in checks)


def test_visual_checks_fail_closed_without_pillow():
    """If Pillow is unavailable the visual gate must fail closed — a gate
    that cannot inspect is not a pass."""
    import visual_qa as vq
    original = vq._inspect_rasterized
    try:
        vq._inspect_rasterized = lambda *a, **k: ["visual inspection unavailable"]
        checks, _ = visual_checks("/nonexistent.pdf")
        assert checks and not checks[0].passed
    finally:
        vq._inspect_rasterized = original


def test_critical_pages_cover_the_consequential_spread():
    """The critical-page set must cover the pages where a rendering defect
    would be most consequential and most likely to be missed by a
    text-only check."""
    required = {"cover", "executive_summary", "technology_profile",
                "swot", "claim_mapping", "operational_audit",
                "chart_heavy", "final_page"}
    assert required.issubset(set(CRITICAL_PAGES))


def test_critical_page_map_tolerates_naming_variants():
    """The novelty section is titled 'IP / Novelty Analysis' in some reports
    and 'Novelty & IP Analysis' in others; claim_mapping must resolve either."""
    from visual_qa import _critical_page_map
    m1 = _critical_page_map({"IP / Novelty Analysis": 7}, 40)
    assert m1["claim_mapping"] == 7
    m2 = _critical_page_map({"Novelty & IP Analysis": 7}, 40)
    assert m2["claim_mapping"] == 7
    m3 = _critical_page_map({}, 40)
    assert m3["claim_mapping"] is None
    assert m3["final_page"] == 40


def test_report_to_dict_is_machine_readable():
    report = run_visual_qa("/nonexistent.pdf", expected_min_pages=1)
    payload = report_to_dict(report)
    assert "passed" in payload
    assert "structural" in payload
    assert "visual" in payload
    assert "rasterized_pages" in payload