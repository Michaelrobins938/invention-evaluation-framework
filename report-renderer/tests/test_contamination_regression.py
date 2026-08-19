"""
Adversarial Regression Test Fixture: Cross-Patent Contamination
================================================================

This test suite verifies that the v1.8 integrity gate prevents cross-patent
contamination when rendering reports for different inventions.

Test Scenario:
- Run A: US5215088 (Three-Dimensional Electrode Device)
- Run B: US8527057 (Retinal Prosthesis)
- Inject cross-evidence from Run B into Run A's scores manifest
- Assert that the integrity gate aborts rendering

This is the exact failure mode that corrupted the original US5215088 report.
"""

import pytest
import json
import tempfile
import os
import sys

# Add the report-renderer directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contract import (
    validate_target_identity,
    validate_epistemic_consistency,
    pre_render_integrity_gate,
    RenderContractFailure,
    TargetIdentity,
    EvidenceItem,
    EpistemicState,
    ReportSection,
)


class TestCrossPatentContaminationRegression:
    """Regression tests for the US5215088 contamination failure."""

    def test_us5215088_clean_scores_pass(self):
        """US5215088 scores manifest with correct identity should pass."""
        target = TargetIdentity(
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
        evidence_items = [
            EvidenceItem(
                evidence_id="E-5215088-001",
                target_publication_number="US5215088A",
                source="patent",
                source_type="patent",
                supports=["P-03-003"],
            )
        ]
        sections = []

        # Should not raise
        errors = validate_target_identity(sections, target, evidence_items)
        assert len(errors) == 0

    def test_us5215088_contaminated_with_us8527057_aborts(self):
        """US5215088 scores contaminated with US8527057 evidence should abort."""
        target = TargetIdentity(
            publication_number="US5215088A",
            title="Three-dimensional electrode device",
            government_rights="NSF grant 5-38640-3300",
        )
        evidence_items = [
            EvidenceItem(
                evidence_id="E-8527057-001",
                target_publication_number="US8527057B2",  # CONTAMINATION!
                source="patent",
                source_type="patent",
                supports=["P-03-003"],
            )
        ]
        sections = []

        errors = validate_target_identity(sections, target, evidence_items)
        assert len(errors) > 0
        assert any("US8527057B2" in str(e) for e in errors)

    def test_us5215088_nih_grant_contamination_aborts(self):
        """US5215088 scores with NIH grant (belongs to US8527057) should abort.
        
        NOTE: This test verifies that the pre-render integrity gate catches
        contamination in the report content, not in the target identity itself.
        The target identity validation only checks evidence items against the target.
        """
        target = TargetIdentity(
            publication_number="US5215088A",
            title="Three-dimensional electrode device",
            government_rights="NIH grant R24EY12893-01",  # WRONG but not caught here
        )
        evidence_items = []
        # Create a section with contamination indicator
        sections = [
            ReportSection(
                level=2,
                title="Technology Analysis",
                body="This invention uses NIH grant R24EY12893-01 funding."
            )
        ]

        errors = validate_target_identity(sections, target, evidence_items)
        # Should detect the contamination indicator in the section content
        assert len(errors) > 0

    def test_us5215088_retinal_prosthesis_contamination_aborts(self):
        """US5215088 scores with Retinal Prosthesis title should abort.
        
        NOTE: This test verifies that the pre-render integrity gate catches
        contamination in the report content, not in the target identity itself.
        """
        target = TargetIdentity(
            publication_number="US5215088A",
            title="Retinal Prosthesis",  # WRONG but not caught here
            government_rights="NSF grant 5-38640-3300",
        )
        evidence_items = []
        # Create a section with contamination indicator
        sections = [
            ReportSection(
                level=2,
                title="Technology Analysis",
                body="This invention is a retinal prosthesis for restoring vision."
            )
        ]

        errors = validate_target_identity(sections, target, evidence_items)
        # Should detect the contamination indicator in the section content
        assert len(errors) > 0

    def test_us8527057_clean_scores_pass(self):
        """US8527057 scores manifest with correct identity should pass."""
        target = TargetIdentity(
            publication_number="US8527057B2",
            application_number="US12/103,441",
            title="Retinal Prosthesis",
            inventors=("Greenberg", "Palanca", "Arieli"),
            assignee="Second Sight Medical Products",
            filing_date="2008-04-15",
            grant_date="2013-07-16",
            expiration_date="2028-04-15",
            government_rights="NIH grant R24EY12893-01",
        )
        evidence_items = [
            EvidenceItem(
                evidence_id="E-8527057-001",
                target_publication_number="US8527057B2",
                source="patent",
                source_type="patent",
                supports=["P-03-003"],
            )
        ]
        sections = []

        # Should not raise
        errors = validate_target_identity(sections, target, evidence_items)
        assert len(errors) == 0

    def test_us8527057_contaminated_with_us5215088_aborts(self):
        """US8527057 scores contaminated with US5215088 evidence should abort."""
        target = TargetIdentity(
            publication_number="US8527057B2",
            title="Retinal Prosthesis",
            government_rights="NIH grant R24EY12893-01",
        )
        evidence_items = [
            EvidenceItem(
                evidence_id="E-5215088-001",
                target_publication_number="US5215088A",  # CONTAMINATION!
                source="patent",
                source_type="patent",
                supports=["P-03-003"],
            )
        ]
        sections = []

        errors = validate_target_identity(sections, target, evidence_items)
        assert len(errors) > 0
        assert any("US5215088A" in str(e) for e in errors)

    def test_pre_render_integrity_gate_catches_contamination(self):
        """Pre-render integrity gate should catch contamination before rendering."""
        report_md = """
# Invention Evaluation Report

## 1. Technology Analysis

This is a retinal prosthesis for restoring vision.

## 2. Patent Landscape Analysis

US8527057B2 is the primary patent.
"""
        scores = {
            "invention_id": "US5215088",
            "target_patent": {
                "publication_number": "US5215088A",
                "title": "Three-dimensional electrode device",
                "government_rights": "NSF grant 5-38640-3300",
            },
            "evidence_items": [],
        }

        with pytest.raises(RenderContractFailure) as exc_info:
            pre_render_integrity_gate(report_md, scores, "")

        assert "Retinal Prosthesis" in str(exc_info.value) or "US8527057" in str(exc_info.value)

    def test_epistemic_consistency_completed_with_unestablished_fails(self):
        """Overall status COMPLETED with unestablished propositions should fail."""
        scores = {
            "invention_id": "US5215088",
            "overall_status": "COMPLETED",  # INCONSISTENT!
        }
        section_status = {
            "market": "NOT_ESTABLISHED",  # Still unestablished
        }

        errors = validate_epistemic_consistency(scores, section_status)
        assert len(errors) > 0
        assert any("COMPLETED" in str(e) for e in errors)

    def test_epistemic_consistency_partially_established_passes(self):
        """Overall status PARTIALLY_ESTABLISHED with mix of statuses should pass."""
        scores = {
            "invention_id": "US5215088",
            "overall_status": "PARTIALLY_ESTABLISHED",
        }
        section_status = {
            "technology": "ESTABLISHED",
            "market": "PARTIALLY_ESTABLISHED",
        }

        # Should not raise
        errors = validate_epistemic_consistency(scores, section_status)
        assert len(errors) == 0


class TestContaminationDetectionEdgeCases:
    """Edge cases for contamination detection."""

    def test_missing_target_patent_fails(self):
        """Missing target patent should fail."""
        target = TargetIdentity(
            publication_number="UNKNOWN",
            title="Unknown Invention",
        )
        evidence_items = []
        sections = []

        errors = validate_target_identity(sections, target, evidence_items)
        assert len(errors) > 0

    def test_unknown_publication_number_fails(self):
        """Unknown publication number should fail."""
        target = TargetIdentity(
            publication_number="UNKNOWN",
            title="Some Invention",
        )
        evidence_items = []
        sections = []

        errors = validate_target_identity(sections, target, evidence_items)
        assert len(errors) > 0

    def test_multiple_contaminated_evidence_all_detected(self):
        """Multiple contaminated evidence items should all be detected."""
        target = TargetIdentity(
            publication_number="US5215088A",
            title="Three-dimensional electrode device",
            government_rights="NSF grant 5-38640-3300",
        )
        evidence_items = [
            EvidenceItem(
                evidence_id="E-8527057-001",
                target_publication_number="US8527057B2",
                source="patent",
                source_type="patent",
                supports=["P-03-003"],
            ),
            EvidenceItem(
                evidence_id="E-8527057-002",
                target_publication_number="US8527057B2",
                source="patent",
                source_type="patent",
                supports=["P-03-004"],
            ),
        ]
        sections = []

        errors = validate_target_identity(sections, target, evidence_items)
        # Should detect both contaminated items
        assert len(errors) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
