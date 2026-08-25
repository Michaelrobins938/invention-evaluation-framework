"""PDF-export degradation tests — missing browser must not invalidate HTML."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RENDERER_DIR = Path(__file__).resolve().parents[1] / "report-renderer"
sys.path.insert(0, str(RENDERER_DIR))

import render_report as rr  # noqa: E402


def test_find_chromium_returns_none_when_no_candidates(monkeypatch):
    monkeypatch.setattr(rr.shutil, "which", lambda name: None)
    assert rr.find_chromium() is None


def test_find_chromium_prefers_explicit_override(monkeypatch):
    seen = []
    monkeypatch.setattr(rr.shutil, "which", lambda name: seen.append(name) or ("/bin/x" if name == "mychrome" else None))
    assert rr.find_chromium("mychrome") == "/bin/x"
    assert seen[0] == "mychrome"


def test_export_pdf_error_names_tried_binaries_and_preserves_html_value(monkeypatch, tmp_path):
    monkeypatch.setattr(rr.shutil, "which", lambda name: None)
    html = tmp_path / "report.html"
    html.write_text("<html>delivered</html>", encoding="utf-8")
    with pytest.raises(RuntimeError) as exc:
        rr.export_pdf(html, tmp_path / "report.pdf")
    msg = str(exc.value)
    assert "chromium" in msg and "--chromium" in msg
    assert "HTML report remains valid" in msg
    # the delivered artifact is untouched by the failure
    assert html.read_text(encoding="utf-8") == "<html>delivered</html>"
