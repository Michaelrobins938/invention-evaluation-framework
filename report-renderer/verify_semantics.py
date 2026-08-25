#!/usr/bin/env python3
"""verify.sh helper: v1.8 semantic scans.

Checks that:
  1. The renderer accounts for every source semantic node in the HTML.
  2. The delivered PDF passes the structural + visual QA gate.

The page count is read from the PDF itself rather than hard-coded: the
US8527057 report is 43 pages and the 7149534 report is 47, so a fixed
count would make the gate fail on any other invention.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def _load_renderer(target: Path):
    sys.path.insert(0, str(target))
    sys.path.insert(0, str(target / "report-renderer"))
    spec = importlib.util.spec_from_file_location(
        "render_report", target / "report-renderer" / "render_report.py")
    rr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rr)
    return rr


def _page_count(pdf_path: Path) -> int:
    info = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
    for line in info.splitlines():
        if line.lower().startswith("pages:"):
            return int(line.split(":")[1].strip())
    return 0


def main(target: Path) -> int:
    from contract import parse_report_ast, account_semantic_nodes
    from visual_qa import run_visual_qa

    D = target / "evaluations/us8527057-v17(Complete-pass)"
    rr = _load_renderer(target)

    md = (D / "report-us8527057-v17.md").read_text(encoding="utf-8")
    scores = json.loads(
        (D / "scores-us8527057-v17.json").read_text(encoding="utf-8"))

    # Mirror the production call site (workers.py::_worker_render): omitting
    # submission_md / v17_artifacts here historically produced false
    # "renderer dropped semantic nodes" failures for the three sections
    # sourced from those arguments.
    submission = (target / "evaluations/us8527057/submission-us8527057.md")
    html = rr.render(
        md,
        (D / "recovery-evidence-us8527057-v17.md").read_text(encoding="utf-8"),
        scores,
        submission_md=submission.read_text(encoding="utf-8") if submission.exists() else None,
        v17_artifacts=str(D))
    errors = account_semantic_nodes(
        parse_report_ast(md), html,
        skip_titles=rr.TEMPLATE_RENDERED | rr.DATA_FRAME_RENDERED)
    if errors:
        print("  [FAIL] renderer dropped semantic nodes:")
        for e in errors:
            print(f"         {e.section}: {e.node} — {e.reason}")
        return 1
    print("  [PASS] every source semantic node is accounted for in the "
          "rendered HTML")

    pages = _page_count(D / "report-us8527057-v17.pdf")
    report = run_visual_qa(
        str(D / "report-us8527057-v17.pdf"),
        expected_headings=(
            "Executive Summary", "v1.7 Control State", "Original Submission",
            "Technology Analysis", "Operational Audit",
            "Evidence Recovery Record", "Sources", "v1.7 Inference Controls",
            "SWOT Analysis", "Landscape & Market Data", "IP / Novelty Analysis",
        ),
        expected_min_pages=pages, expected_max_pages=pages)
    if not report.passed:
        print("  [FAIL] visual QA gate did not pass:")
        for c in report.structural:
            if not c.passed:
                print(f"         structural {c.name}: {c.detail}")
        for c in report.visual:
            if not c.passed:
                print(f"         visual {c.page}: {c.issues}")
        return 1
    print(f"  [PASS] visual QA gate passed ({len(report.rasterized_pages)} "
          f"pages rasterized and inspected)")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))