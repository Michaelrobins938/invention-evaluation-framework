#!/usr/bin/env python3
"""
test_contamination_detection.py — Adversarial test for cross-patent contamination.

This test verifies that the pipeline ABORTS (not warns, not downgrades) when
foreign evidence from a different patent is detected in a run.

Usage:
    pytest test_contamination_detection.py -v
"""

import json
import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract import (
    TargetIdentity,
    EvidenceItem,
    validate_target_identity,
    validate_epistemic_consistency,
    pre_render_integrity_gate,
    RenderContractFailure,
    parse_report_ast,
)


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

US5215088_TARGET = TargetIdentity(
    publication_number="US5215088A",
    application_number="US07/432992",
    title="Three-dimensional electrode device",
    inventors=("Normann", "Campbell", "Jones"),
    assignee="University of Utah",
    filing_date="1989-11-07",
    grant_date="1993-06-01",
    expiration_date="2010-06-01",
    government_rights="NSF grant 5-38640-3300",
)

US8527057_TARGET = TargetIdentity(
    publication_number="US8527057B2",
    application_number="US12/016,056",
    title="Retinal prosthesis",
    inventors=("Greenberg", "Ok", "Neysmith", "Wilkins", "Talbot", "Chang"),
    assignee="Second Sight Medical Products",
    filing_date="2008-01-17",
    grant_date="2013-09-03",
    expiration_date="2028-01-17",
    government_rights="NIH grant R24EY12893-01",
)

US5215088_EVIDENCE = [
    EvidenceItem(
        evidence_id="E-05-001",
        target_publication_number="US5215088A",
        source="Najafi & Wise 1985",
        source_type="patent",
        supports=["P-05-001"],
        confidence="HIGH",
    ),
    EvidenceItem(
        evidence_id="E-06-001",
        target_publication_number="US5215088A",
        source="PMC8981395",
        source_type="literature",
        supports=["P-06-005"],
        confidence="HIGH",
    ),
]

US8527057_EVIDENCE = [
    EvidenceItem(
        evidence_id="E-8527057-001",
        target_publication_number="US8527057B2",
        source="Greenberg et al. 2013",
        source_type="patent",
        supports=["P-8527057-001"],
        confidence="HIGH",
    ),
]


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

class TestTargetIdentityFirewall:
    """Verify that foreign evidence is detected and rejected."""
    
    def test_clean_run_passes(self):
        """Valid evidence for target patent should pass."""
        errors = validate_target_identity(
            sections=[],
            target=US5215088_TARGET,
            evidence_items=US5215088_EVIDENCE,
        )
        assert errors == [], f"Clean run should pass, got: {errors}"
    
    def test_foreign_evidence_detected(self):
        """Evidence from US8527057 in a US5215088 run must be flagged."""
        contaminated_evidence = US5215088_EVIDENCE + US8527057_EVIDENCE
        
        errors = validate_target_identity(
            sections=[],
            target=US5215088_TARGET,
            evidence_items=contaminated_evidence,
        )
        
        assert len(errors) > 0, "Should detect foreign evidence"
        assert any("US8527057B2" in str(e) for e in errors), \
            "Error should reference the foreign patent"
        assert any("FATAL" in str(e) for e in errors), \
            "Error should be marked as FATAL"
    
    def test_all_foreign_evidence_detected(self):
        """All foreign evidence items should be flagged, not just the first."""
        contaminated_evidence = US5215088_EVIDENCE + US8527057_EVIDENCE
        
        errors = validate_target_identity(
            sections=[],
            target=US5215088_TARGET,
            evidence_items=contaminated_evidence,
        )
        
        # Should have at least one error per foreign evidence item
        foreign_errors = [e for e in errors if "US8527057B2" in str(e)]
        assert len(foreign_errors) >= 1, \
            f"Expected at least 1 foreign evidence error, got {len(foreign_errors)}"
    
    def test_missing_target_fails(self):
        """Run without target patent should fail."""
        errors = validate_target_identity(
            sections=[],
            target=TargetIdentity(publication_number="UNKNOWN"),
            evidence_items=[],
        )
        
        assert len(errors) > 0, "Missing target should fail"
        assert any("UNKNOWN" in str(e) for e in errors), \
            "Error should reference UNKNOWN target"


class TestContaminationDetection:
    """Verify that hardcoded contamination patterns are detected."""
    
    def test_nih_grant_contamination(self):
        """NIH grant R24EY12893-01 should trigger contamination alert."""
        from contract import parse_report_ast, validate_target_identity
        
        # Simulate a report with contamination
        contaminated_report = """
## Technology Analysis

US 8,527,057 B2 — Retinal Prosthesis

This invention relates to a retinal prosthesis.

Government rights: NIH grant R24EY12893-01
"""
        
        sections = parse_report_ast(contaminated_report)
        errors = validate_target_identity(
            sections=sections,
            target=US5215088_TARGET,
            evidence_items=[],
        )
        
        # Should detect contamination indicators
        contamination_errors = [e for e in errors if "Contamination" in e.section]
        assert len(contamination_errors) > 0, \
            "Should detect NIH grant contamination"
    
    def test_retinal_prosthesis_contamination(self):
        """Retinal Prosthesis title should trigger contamination alert."""
        from contract import parse_report_ast, validate_target_identity
        
        contaminated_report = """
## Market Analysis

The Retinal Prosthesis market is growing rapidly.

Second Sight Medical Products is the market leader.
"""
        
        sections = parse_report_ast(contaminated_report)
        errors = validate_target_identity(
            sections=sections,
            target=US5215088_TARGET,
            evidence_items=[],
        )
        
        contamination_errors = [e for e in errors if "Contamination" in e.section]
        assert len(contamination_errors) > 0, \
            "Should detect Retinal Prosthesis contamination"


class TestEpistemicConsistency:
    """Verify that epistemic state contradictions are detected."""
    
    def test_completed_with_unestablished_fails(self):
        """COMPLETED status with NOT_ESTABLISHED sections should fail."""
        scores = {
            "overall_status": "COMPLETED",
            "section_status": {
                "Market Analysis": "NOT_ESTABLISHED",
                "Competitive Landscape": "NOT_ESTABLISHED",
            },
        }
        
        errors = validate_epistemic_consistency(
            scores=scores,
            section_status=scores["section_status"],
        )
        
        assert len(errors) > 0, "Should detect contradiction"
        assert any("Contradiction" in str(e) for e in errors), \
            "Error should reference contradiction"
    
    def test_derived_metric_without_evidence_fails(self):
        """Market claims without evidence should fail."""
        scores = {
            "overall_status": "COMPLETED",
            "market_claims": {
                "market_size": 3.25,
                "growth_rate": 14.5,
            },
            "evidence_items": [],  # No evidence
        }
        
        errors = validate_epistemic_consistency(
            scores=scores,
            section_status={},
        )
        
        assert len(errors) > 0, "Should detect derived metrics without evidence"


class TestPreRenderIntegrityGate:
    """Verify that the full integrity gate catches all issues."""
    
    def test_clean_report_passes(self):
        """Clean report should pass integrity gate."""
        clean_scores = {
            "target_patent": {
                "publication_number": "US5215088A",
                "title": "Three-dimensional electrode device",
                "government_rights": "NSF grant 5-38640-3300",
            },
            "evidence_items": [
                {
                    "evidence_id": "E-05-001",
                    "target_publication_number": "US5215088A",
                    "source": "Najafi & Wise 1985",
                    "source_type": "patent",
                    "supports": ["P-05-001"],
                    "confidence": "HIGH",
                },
            ],
        }
        
        clean_report = """
## Executive Summary

This evaluation covers US5215088.

## 1. Technology Analysis

The patent describes a three-dimensional electrode device.
"""
        
        # Should not raise
        try:
            pre_render_integrity_gate(clean_report, clean_scores, "")
        except RenderContractFailure:
            pytest.fail("Clean report should pass integrity gate")
    
    def test_contaminated_report_aborts(self):
        """Contaminated report must ABORT, not warn."""
        contaminated_scores = {
            "target_patent": {
                "publication_number": "US5215088A",
                "title": "Three-dimensional electrode device",
                "government_rights": "NSF grant 5-38640-3300",
            },
            "evidence_items": [
                {
                    "evidence_id": "E-8527057-001",
                    "target_publication_number": "US8527057B2",
                    "source": "Greenberg et al. 2013",
                    "source_type": "patent",
                    "supports": ["P-8527057-001"],
                    "confidence": "HIGH",
                },
            ],
        }
        
        contaminated_report = """
## Executive Summary

This evaluation covers US5215088.

Government rights: NIH grant R24EY12893-01
"""
        
        # Must RAISE, not return errors
        with pytest.raises(RenderContractFailure) as exc_info:
            pre_render_integrity_gate(contaminated_report, contaminated_scores, "")
        
        error_msg = str(exc_info.value)
        assert "FATAL" in error_msg, "Should be marked FATAL"
        assert "US8527057B2" in error_msg, "Should reference foreign patent"
        assert "halted" in error_msg.lower(), "Should indicate halt"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
