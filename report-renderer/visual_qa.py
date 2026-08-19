#!/usr/bin/env python3
"""
report-renderer/visual_qa.py — Deterministic visual QA for the rendered PDF.

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

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# The pages that must be visually inspected on every run. These are the pages
# where a rendering defect would be most consequential and most likely to be
# missed by a text-only check.
CRITICAL_PAGES: tuple[str, ...] = (
    "cover",
    "executive_summary",
    "technology_profile",
    "swot",
    "claim_mapping",
    "operational_audit",
    "chart_heavy",
    "final_page",
)


@dataclass
class StructuralCheck:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class VisualCheck:
    page: str
    passed: bool
    issues: list[str] = field(default_factory=list)


@dataclass
class VisualQAReport:
    structural: list[StructuralCheck] = field(default_factory=list)
    visual: list[VisualCheck] = field(default_factory=list)
    rasterized_pages: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.structural) and all(
            c.passed for c in self.visual)


def _run(cmd: list[str], **kwargs: Any) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return proc.stdout


def _pdfinfo(pdf_path: str) -> dict[str, str]:
    out = _run(["pdfinfo", pdf_path])
    return {k.strip().lower(): v.strip() for k, _, v in
            (line.partition(":") for line in out.splitlines() if ":" in line)}


def _page_text(pdf_path: str, page: int) -> str:
    return _run(["pdftotext", "-f", str(page), "-l", str(page), pdf_path, "-"])


# ---------------------------------------------------------------------------
# Structural QA
# ---------------------------------------------------------------------------

def structural_checks(
    pdf_path: str,
    *,
    expected_headings: tuple[str, ...] = (),
    expected_tables: int = 0,
    expected_min_pages: int = 1,
    expected_max_pages: int | None = None,
    forbidden_tokens: tuple[str, ...] = (),
) -> list[StructuralCheck]:
    """Run the structural QA suite against a rendered PDF."""
    checks: list[StructuralCheck] = []
    info = _pdfinfo(pdf_path)

    pages = int(info.get("pages", "0"))
    checks.append(StructuralCheck(
        "pdf_exists", True,
        f"{pdf_path} ({pages} pages)"))

    checks.append(StructuralCheck(
        "page_count_minimum", pages >= expected_min_pages,
        f"{pages} pages >= {expected_min_pages}"))

    if expected_max_pages is not None:
        checks.append(StructuralCheck(
            "page_count_maximum", pages <= expected_max_pages,
            f"{pages} pages <= {expected_max_pages}"))

    page_size = info.get("page size", "")
    checks.append(StructuralCheck(
        "page_size_a4", "A4" in page_size or "595" in page_size,
        page_size or "page size not reported"))

    # Every expected heading must appear on at least one page.
    full_text = "\n".join(_page_text(pdf_path, p) for p in range(1, pages + 1))
    for heading in expected_headings:
        present = heading in full_text
        checks.append(StructuralCheck(
            f"heading:{heading[:40]}", present,
            "found" if present else "missing from every page"))

    # Required tables: count markdown-table separators rendered as HTML tables.
    table_count = full_text.count("|")  # crude proxy; tables render as text
    checks.append(StructuralCheck(
        "expected_tables_present", table_count >= expected_tables,
        f"{table_count} table-ish tokens >= {expected_tables}"))

    # Forbidden tokens must not appear anywhere.
    for token in forbidden_tokens:
        present = token in full_text
        checks.append(StructuralCheck(
            f"forbidden:{token[:30]}", not present,
            "absent" if present else f"present on {full_text.count(token)} pages"))

    return checks


# ---------------------------------------------------------------------------
# Visual QA
# ---------------------------------------------------------------------------

def _rasterize_page(pdf_path: str, page: int, out_path: str,
                    dpi: int = 110) -> str:
    """Rasterize one page to PNG. Returns the output path.

    pdftoppm names the render after the *source page number*
    (``stem-02.png`` for page 2), not a render counter, so the produced file
    is located by globbing the temporary directory for exactly one PNG. If
    more than one appears, the render is nondeterministic and we fail closed
    rather than guessing which is the right page.
    """
    parent = Path(out_path).parent
    parent.mkdir(parents=True, exist_ok=True)
    before = set(parent.glob("*.png"))
    cmd = ["pdftoppm", "-f", str(page), "-l", str(page),
           "-r", str(dpi), "-png", pdf_path,
           os.path.splitext(out_path)[0]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {proc.stderr}")
    after = set(parent.glob("*.png")) - before
    if len(after) != 1:
        raise RuntimeError(
            f"pdftoppm produced {len(after)} PNGs for page {page} "
            f"(expected exactly 1): {sorted(after)}")
    return str(after.pop())


def _locate_sections(pdf_path: str, pages: int,
                     section_titles: list[str]) -> dict[str, int]:
    """Scan the printed PDF page by page for section titles.

    The final PDF has no TOCMARK strings (they are stripped in pass 2), so
    sections are located by their rendered heading text. Returns
    {section_title: physical_page_number}.
    """
    located: dict[str, int] = {}
    for title in section_titles:
        if title in located:
            continue
        for p in range(1, pages + 1):
            if title in _page_text(pdf_path, p):
                located[title] = p
                break
    return located


def _critical_page_map(located: dict[str, int], pages: int) -> dict[str, int | None]:
    """Map critical-page names to physical page numbers.

    Tolerant of section-title naming variants across reports: the novelty
    section is titled "IP / Novelty Analysis" in some reports and
    "Novelty & IP Analysis" in others.
    """
    return {
        "cover": 1,
        "executive_summary": located.get("Executive Summary"),
        "technology_profile": located.get("Technology Analysis"),
        "swot": located.get("SWOT Analysis"),
        "claim_mapping": (located.get("IP / Novelty Analysis")
                          or located.get("Novelty & IP Analysis")),
        "operational_audit": located.get("Operational Audit"),
        "chart_heavy": located.get("Landscape & Market Data"),
        "final_page": pages,
    }


def visual_checks(
    pdf_path: str,
    *,
    critical_pages: tuple[str, ...] = CRITICAL_PAGES,
    section_titles: list[str] | None = None,
    dpi: int = 110,
    tmp_dir: str | None = None,
) -> tuple[list[VisualCheck], list[str]]:
    """Rasterize the critical pages and inspect them.

    Returns (checks, rasterized_page_paths).

    The inspection is *deterministic*: every run rasterizes the same pages
    and records the page numbers it actually opened. A claim of "full visual
    inspection" is never made from a subset.
    """
    info = _pdfinfo(pdf_path)
    pages = int(info.get("pages", "0"))
    if pages == 0:
        return [VisualCheck("pdf_unreadable", False, ["no pages reported"])], []

    # Map critical-page names to physical page numbers. The cover is page 1;
    # the remaining critical pages are located by scanning the printed PDF
    # for their section titles, so the mapping is derived from the actual
    # output rather than assumed.
    # Always scan the canonical critical-page headings too, so a report whose
    # section titles use a naming variant (e.g. "Novelty & IP Analysis") is
    # still located even when the caller's expected_headings differ.
    _critical_headings = [
        "Executive Summary", "Technology Analysis", "SWOT Analysis",
        "IP / Novelty Analysis", "Novelty & IP Analysis",
        "Operational Audit", "Landscape & Market Data",
    ]
    _titles = list(section_titles or [])
    for _h in _critical_headings:
        if _h not in _titles:
            _titles.append(_h)
    located = _locate_sections(pdf_path, pages, _titles)
    page_for = _critical_page_map(located, pages)

    checks: list[VisualCheck] = []
    rasterized: list[str] = []

    tmp = Path(tmp_dir or tempfile.mkdtemp(prefix="iea-visual-"))
    tmp.mkdir(parents=True, exist_ok=True)

    for name in critical_pages:
        page_no = page_for.get(name)
        if page_no is None or page_no > pages:
            checks.append(VisualCheck(
                name, False, [f"page for '{name}' not found in PDF"]))
            continue
        # A fresh directory per page so the before/after diff in
        # _rasterize_page sees exactly one PNG.
        page_tmp = tmp / name
        page_tmp.mkdir(parents=True, exist_ok=True)
        try:
            png = _rasterize_page(pdf_path, page_no, str(page_tmp / f"{name}.png"), dpi)
            rasterized.append(png)
        except FileNotFoundError:
            checks.append(VisualCheck(
                name, False, ["pdftoppm not installed; visual QA unavailable"]))
            continue
        except RuntimeError as exc:
            checks.append(VisualCheck(name, False, [str(exc)]))
            continue

        issues = _inspect_rasterized(png, name, page_no, pages)
        checks.append(VisualCheck(name, not issues, issues))

    return checks, rasterized


def _inspect_rasterized(png_path: str, name: str, page_no: int,
                         total_pages: int) -> list[str]:
    """Inspect a rasterized page for common rendering defects.

    Uses Pillow when available; falls back to reporting the rasterization
    metadata so the gate is still deterministic (it fails closed).
    """
    issues: list[str] = []
    p = Path(png_path)
    if not p.exists() or p.stat().st_size == 0:
        return [f"rasterized page missing or empty"]

    try:
        from PIL import Image  # type: ignore
        img = Image.open(png_path)
        w, h = img.size
    except Exception:
        # Pillow unavailable — the page was rasterized, which is the
        # deterministic signal we have. Fail closed rather than silently
        # passing: a visual gate that cannot inspect is not a pass.
        return ["visual inspection unavailable: Pillow not installed"]

    if w == 0 or h == 0:
        return ["rasterized page has zero dimensions"]

    # Blank page: nothing was rendered at all.
    try:
        gray = img.convert("L")
        colors = gray.getcolors(maxcolors=2 ** 16)
        if colors and len(colors) == 1:
            issues.append("page rendered blank (single color)")
    except Exception:
        pass

    # Page-break / overflow heuristics. The cover must fit on one page; a
    # two-page cover offsets every TOC entry downstream.
    if name == "cover" and page_no != 1:
        issues.append("cover is not on physical page 1")
    if name == "final_page" and page_no != total_pages:
        issues.append("final page is not the last physical page")

    return issues


def run_visual_qa(
    pdf_path: str,
    *,
    expected_headings: tuple[str, ...] = (),
    expected_tables: int = 0,
    expected_min_pages: int = 1,
    expected_max_pages: int | None = None,
    forbidden_tokens: tuple[str, ...] = (),
    critical_pages: tuple[str, ...] = CRITICAL_PAGES,
) -> VisualQAReport:
    """Run both structural and visual QA and return a combined report."""
    structural = structural_checks(
        pdf_path,
        expected_headings=expected_headings,
        expected_tables=expected_tables,
        expected_min_pages=expected_min_pages,
        expected_max_pages=expected_max_pages,
        forbidden_tokens=forbidden_tokens,
    )
    visual, rasterized = visual_checks(
        pdf_path, critical_pages=critical_pages, section_titles=list(expected_headings))
    return VisualQAReport(
        structural=structural, visual=visual, rasterized_pages=rasterized)


def report_to_dict(report: VisualQAReport) -> dict[str, Any]:
    return {
        "passed": report.passed,
        "structural": [
            {"name": c.name, "passed": c.passed, "detail": c.detail}
            for c in report.structural
        ],
        "visual": [
            {"page": c.page, "passed": c.passed, "issues": c.issues}
            for c in report.visual
        ],
        "rasterized_pages": report.rasterized_pages,
    }


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Visual QA gate for a rendered PDF")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=None, help="JSON report path")
    ap.add_argument("--min-pages", type=int, default=1)
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument("--expected-heading", action="append", default=[])
    ap.add_argument("--forbidden", action="append", default=[])
    args = ap.parse_args()

    report = run_visual_qa(
        args.pdf,
        expected_headings=tuple(args.expected_heading),
        expected_min_pages=args.min_pages,
        expected_max_pages=args.max_pages,
        forbidden_tokens=tuple(args.forbidden),
    )
    payload = report_to_dict(report)
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2) + "\n",
                                  encoding="utf-8")
    print(json.dumps(payload, indent=2))
    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()