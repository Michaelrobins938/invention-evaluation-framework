from engine_v17.migration import migrate_v16_artifact
from engine_v17.models import ResolutionState


def test_v16_exhausted_requires_v17_migration_review():
    result = migrate_v16_artifact({"id": "P-04-001", "state": "EXHAUSTED"})
    assert result.state == ResolutionState.MIGRATION_REQUIRED
    assert result.migration_metadata["legacy_state"] == "EXHAUSTED"
