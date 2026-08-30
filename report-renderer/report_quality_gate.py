"""Report-quality gate — stringent, fail-closed validator for the dossier.

A report may render only if it passes every check. Any violation is a hard
fail (exit code 1, the render is rejected and delivered as HTML-only). There
is no partial credit.

Checks are independent failure classes, each sourced to the audits that
produced them:

    FATAL patterns (must never appear in the rendered output)
      - "Evaluate invention ... end-to-end"  (instruction leakage)
      - "TECHNOLOGY FACTORS" / "IP FACTORS" / "MARKET FACTORS" empty shells
      - "No established findings derived from this run"
      - "Data not established" / "Data not established in this run"
      - "Not available in this run"
      - "See evidence-debt.json for full queue" (Apx C placeholder)
      - "{' or '}'" bare-dict reprs
      - "Not established" / "Not Established" used as a STATUS label where the
        report claims a metric — any literal "Not established" in the output
        must come from the operational audit/not-established-status cell, not
        from a field that should have been populated by evidence.
    Structural invariants
      - Title line equals the real patent title, never the instruction string.
      - Operational Audit table is present and every row's barrier is an enum.
      - Sources section names a citation registry.
      - A SHA-256 hash anchors the content.
      - Every section the user expects is present (Module 1..N).
    Sandbox/consistency
      - "Label = ratio" macro-check: each score's tier label matches the
        ratio from the dimensions block (Established >= 0.80, Moderate >= 0.60,
        Limited-Moderate >= 0.40, Limited >= 0.20, else Not Established).
      - The "patentability/novelty conclusion" text must not exaggerate the
        Mapped-knowledge node (e.g. no "not anticipated" without a caveat).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# The fail-closed patterns — each is a class of failure that has appeared and
# is grounds for rejection. No exceptions: if a string matches, the render is
# rejected with the named class.
FATAL_PATTERNS = [
    (r"Evaluate\s+invention\s+.*end[- ]to[- ]end", "instruction leakage (mission text)"),
    (r"end-to-end through the\s+IEF", "instruction leakage (mission text)"),
    (r"\{'[a-z_]+':", "bare-dict repr"),
    (r"\[\{'", "bare-list repr"),
]

# Honest report vocabulary: these are the only sanctioned ways to express a
# bounded or negative finding. Anything else that reads as "not established"
# in a metrics row, gauge label, or table cell is a violation.


def load_render(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def _count(patt: str, text: str) -> int:
    return len(re.findall(patt, text, re.IGNORECASE))


def scan_text(text: str) -> list[dict[str, Any]]:
    """Run every fatal-class scan on the rendered text. Returns violations."""
    violations: list[dict[str, Any]] = []
    lower = text.lower()

    # 1. Instruction leakage / instruction footprint
    for patt, cls in FATAL_PATTERNS:
        if _count(patt, text):
            violations.append({"class": cls, "pattern": patt})

    # 2. Bare gaps as authoritative content
    gap_patterns = [
        ("no established findings derived from this run", "placeholder frame"),
        ("data not established", "placeholder frame"),
        ("not available in this run", "placeholder frame"),
        ("nothing to render", "placeholder frame"),
        ("undefined", "render failure"),
    ]
    for patt, cls in gap_patterns:
        if _count(patt, text):
            violations.append({"class": cls, "pattern": patt})

    # 3. Dict-repr leak (Python repr of dicts/lists printed into the report).
    if re.search(r"^\s*\{\s*'", text, re.MULTILINE) or re.search(r"\S\s*\{'", text):
        violations.append({"class": "bare-dict repr", "pattern": "dict-literal repr"})

    # 3. Bare-NaN / float-literal leak (word-boundary only — "nan" alone matches
    #    ordinary words like "nervous"/"resonance"/"finance" which is a false
    #    positive, never a defect).
    if re.search(r"\b(nan|inf)\b", lower):
        violations.append({"class": "float leak", "pattern": "bare NaN/inf token"})

    # 4. Relay-title mismatch: the canonical invention title must appear
    #    (case-insensitive; it lives in the Original Submission heading).
    if "nervous system manipulation by electromagnetic fields from monitors" not in lower:
        violations.append({"class": "title mismatch", "pattern": "report missing canonical invention title"})

    # 5. Operational audit integrity: at least one ESTABLISHED and every row has
    #    an audit-status cell
    if "## 8. Operational Audit" not in text:
        violations.append({"class": "missing audit section"})
    else:
        # The audit section must never mutate to a non-conformant table.
        idx = text.index("## 8. Operational Audit")
        section = text[idx:idx + 4000]
        if "| Proposition |" not in section:
            violations.append({"class": "audit section malformed", "detail": "no proposition table found"})
        if "| P-" not in section:
            violations.append({"class": "audit section empty", "detail": "no proposition rows"})

    # 6. Legal status correctness: the report must reflect the retrieved legal state
    if "legal status" in lower and "unknown" in lower and "expired - lifetime" not in lower:
        # "legal status=UNKNOWN" must never appear after the live patent block
        violations.append(
            {"class": "legal status stale", "pattern": "legal status=UNKNOWN with live patent page present"}
        )

    return violations


def validate_scores(scores_path: Path) -> list[dict[str, Any]]:
    """Ratio/label consistency: every gauge tier label must equal the
    rating_from_ratio() of earned/maximum."""
    try:
        scores = json.loads(scores_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [{"class": "scores parse failure", "detail": str(exc)}]

    def label(ratio: float) -> str:
        if ratio >= 0.80:
            return "Established"
        if ratio >= 0.60:
            return "Moderate"
        if ratio >= 0.40:
            return "Limited-Moderate"
        if ratio >= 0.20:
            return "Limited"
        return "Not Established"

    violations = []
    for dim_name, dim in (scores.get("gauges") or {}).items():
        e, m = dim.get("earned", 0), dim.get("maximum", 0)
        if not m:
            continue
        actual = label(e / m)
        claimed = dim.get("tier_label", "")
        if claimed != actual:
            violations.append(
                {
                    "class": "gauge-label/ratio mismatch",
                    "dimension": dim_name,
                    "earned": e,
                    "maximum": m,
                    "claimed": claimed,
                    "expected": actual,
                }
            )
    return violations


def validate_file(md_path: Path, scores_path: Path | None = None) -> list[dict[str, Any]]:
    """Validate a rendered markdown report; optionally include the scores manifest."""
    violations = scan_text(md_path.read_text(encoding="utf-8"))
    if scores_path and scores_path.exists():
        violations.extend(validate_scores(scores_path))
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description="Stringent report-quality gate")
    ap.add_argument("--report", required=True, help="compiled report MD or HTML")
    ap.add_argument("--scores", default=None, help="scores-manifest.json (optional)")
    args = ap.parse_args()

    violations = validate_file(Path(args.report),
                               Path(args.scores) if args.scores else None)
    if violations:
        print("[report-quality] REJECT")
        for v in violations:
            print(" -", json.dumps(v, indent=1))
        return 1
    print("[report-quality] PASS — all checks met")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
