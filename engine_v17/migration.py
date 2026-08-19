"""Migration helpers for v1.6 artifacts and v1.8 -> v1.9 ledgers."""

from .models import (
    EpistemicState, Proposition, RecoveryState, Scope,
    ResolutionState, lattice_from_legacy,
)


def migrate_v16_artifact(data: dict) -> Proposition:
    return Proposition.from_dict(data)


def migrate_v18_ledger(ledger: dict) -> dict:
    """Add v1.9 lattice fields to every proposition entry.

    Keeps the legacy ``status`` key so v1.8 consumers still work. Entries
    that already carry ``epistemic_state``/``recovery_state`` are left
    untouched; only missing fields are filled from the legacy state.
    """
    raw = ledger.get("proposition_ledger", ledger)
    out = dict(ledger)
    migrated = {}
    for pid, entry in raw.items():
        e = dict(entry)
        if "epistemic_state" not in e:
            status = str(e.get("status", e.get("state", "UNRESOLVED")))
            # If status is already a canonical epistemic state, use it directly
            # and derive the recovery state from it (ESTABLISHED -> NONE_REQUIRED).
            # Otherwise map the legacy ResolutionState value through the lattice.
            try:
                epi = EpistemicState(status.upper())
                e["epistemic_state"] = epi.value
                default_rec = (RecoveryState.NONE_REQUIRED
                               if epi == EpistemicState.ESTABLISHED
                               else RecoveryState.SEARCH_PENDING)
                e["recovery_state"] = e.get("recovery_state", default_rec.value)
            except ValueError:
                legacy = ResolutionState(status.lower())
                epi, rec = lattice_from_legacy(legacy)
                e["epistemic_state"] = epi.value
                e["recovery_state"] = e.get("recovery_state", rec.value)
        e.setdefault("recovery_state", RecoveryState.NONE_REQUIRED.value)
        e.setdefault("scope", Scope.TARGET_PATENT.value)
        migrated[pid] = e
    out["proposition_ledger"] = migrated
    return out
