"""Migration helpers for v1.6 artifacts."""

from .models import Proposition


def migrate_v16_artifact(data: dict) -> Proposition:
    return Proposition.from_dict(data)
