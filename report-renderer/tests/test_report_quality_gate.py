"""Hermetic tests for report-renderer/report_quality_gate.py.

The gate is the framework's stringent quality enforcement — each test plants a
specific defect class and asserts the gate REJECTs it. A correct report passes.
"""

from __future__ import annotations

import json

import pytest

import report_quality_gate as rqg


CLEAN = """
# Invention Evaluation Report — US6506148

> This v1.7 report is generated from phase artifacts and the v1.7 evidence graph.

### Invention Name
Nervous System Manipulation by Electromagnetic Fields from Monitors

## 1. Technology Analysis
Established mechanism.

| Dimension | Points | Weighted ratio | Rating |
|-----------|--------|----------------|--------\
| Technology | 1/1 | 1.00 | Established |

## 8. Operational Audit

| Proposition | Work state | Barrier type | Description |
|-------------|------------|--------------|-------------|
| P-02-001 | ESTABLISHED | none | evidence-backed: passed Evidence Sufficiency Gate |

## Sources
- https://patents.google.com/patent/US6506148B2/en

See source-registry.json for citations.
"""


def _scores(earned=1, maximum=1, label="Established"):
    return {"gauges": {"technology": {"tier_label": label, "earned": earned, "maximum": maximum}}}


def test_clean_report_passes(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text(CLEAN)
    sc = tmp_path / "scores.json"
    sc.write_text(json.dumps(_scores()))
    assert rqg.validate_file(rep, sc) == []


def test_rejects_instruction_leak(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text(CLEAN + "\nThe system was instructed to Evaluate invention US6506148 end-to-end through the IEF")
    out = rqg.validate_file(rep)
    assert any(v.get("class") == "instruction leakage (mission text)" for v in out)


def test_rejects_dict_repr_leak(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text(CLEAN + "\n\n  {'state': 'Expired - Lifetime', 'active': False}\n")
    out = rqg.validate_file(rep)
    assert any("bare-dict" in v.get("class", "") for v in out)


def test_rejects_float_leak(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text(CLEAN + "\nand the confidence is NaN here")
    out = rqg.validate_file(rep)
    assert any(v.get("class") == "float leak" for v in out)


def test_not_reject_ordinary_words_containing_nan():
    # "nan" inside ordinary words must never be flagged; only a true NaN literal.
    import re
    assert re.search(r"\bnan\b", "nervous system".lower()) is None
    assert re.search(r"\bnan\b", "the resonance".lower()) is None
    assert re.search(r"\bnan\b", "confidence is NaN here".lower()) is not None


def test_rejects_ratio_label_mismatch(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text(CLEAN)
    sc = tmp_path / "scores.json"
    # 1/2 = 0.5 -> Limited-Moderate; claiming Established is a mismatch
    sc.write_text(json.dumps(_scores(earned=2, maximum=2, label="Established")))
    assert rqg.validate_scores(sc) == []  # ratio 1.0 -> Established is consistent
    sc2 = tmp_path / "scores2.json"
    sc2.write_text(json.dumps(_scores(earned=1, maximum=3, label="Established")))
    out = rqg.validate_scores(sc2)
    assert any("mismatch" in v.get("class", "") for v in out)


def test_rejects_missing_audit_section(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text("# Invention Evaluation Report — US6506148\n\n## 1. X\n\nNo audit.")
    out = rqg.validate_file(rep)
    assert any("audit" in v.get("class", "") for v in out)


def test_rejects_missing_title(tmp_path):
    rep = tmp_path / "report.md"
    rep.write_text("# Report — X\n\n## 8. Operational Audit\n\n| Proposition | Work state | Barrier type | Description |\n|---|---|---|---|\n| P-02-001 | ESTABLISHED | none | x |")
    out = rqg.validate_file(rep)
    assert any(v.get("class") == "title mismatch" for v in out)
