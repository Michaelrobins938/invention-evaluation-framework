"""Deterministic report-integrity scans — E9 hardening.

Catches the report-defect classes that text generation introduces even when
upstream evidence discipline held:

  1. Template-placeholder leakage   → [RELEVANT POC WILL BE LINKED HERE]
  2. Proposition-ID collisions      → same ID bound to two different subjects
  3. Barrier-column misuse          → descriptions where barrier enums belong
  4. Missing executive structure    → no Rating Methodology / Key Evidence / Legend

These are pipeline defects (BLOCK delivery), never evidence debt: a report that
fails these scans is not deliverable in any state.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# Canonical barrier vocabulary (mirrors epistemic_gates usage).
BARRIER_TYPES: frozenset[str] = frozenset({
    "source_unavailable",
    "insufficient_identity",
    "insufficient_search_completion",
    "insufficient_corroboration",
    "insufficient_temporal_match",
    "unresolved_conflict",
    "scope_mismatch",
    "insufficient_technical_demonstration",
})

WORK_STATES: frozenset[str] = frozenset({
    "SEARCHING", "ESCALATING", "REQUIRES VERIFICATION",
    "ESCALATION_REQUIRED", "SEARCH_EXHAUSTED", "EXHAUSTED", "BLOCKED", "WORK QUEUE",
    # models.RecoveryState members (the canonical work-state axis):
    "NONE_REQUIRED", "SEARCH_PENDING", "UNAVAILABLE_BY_CONSTRAINT",
})

REQUIRED_EXEC_SECTIONS: tuple[str, ...] = (
    "Rating Methodology",
    "Key Evidence Supporting the Ratings",
    "Proposition Identifier Legend",
)

# [UPPERCASE PLACEHOLDER] with at least one internal space or 5+ chars —
# deliberately ignores lowercase bracketed placeholders like "[date]".
_PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9][A-Z0-9 _\-]{3,}\]")

# Proposition IDs: P-02-001, P-05-008a, A-02-004 (avenue records)
_PROP_ID_RE = re.compile(r"\b([PA])-(\d{2})-(\d{3})([a-z])?\b")


@dataclass
class IntegrityReport:
    """Aggregated result of all integrity scans."""

    placeholders: list[str] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)
    invalid_barriers: list[dict[str, Any]] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (
            self.placeholders or self.duplicate_ids
            or self.invalid_barriers or self.missing_sections
        )

    def summary(self) -> str:
        if self.clean:
            return "report integrity: CLEAN"
        parts = []
        if self.placeholders:
            parts.append(f"{len(self.placeholders)} placeholder(s): {self.placeholders[:3]}")
        if self.duplicate_ids:
            parts.append(f"colliding proposition IDs: {sorted(set(self.duplicate_ids))}")
        if self.invalid_barriers:
            parts.append(f"{len(self.invalid_barriers)} invalid barrier_type value(s)")
        if self.missing_sections:
            parts.append(f"missing sections: {self.missing_sections}")
        return "report integrity: FAILED — " + "; ".join(parts)


def scan_placeholders(text: str) -> list[str]:
    """Return template-placeholder residue found in rendered report text."""
    return sorted({m.group(0) for m in _PLACEHOLDER_RE.finditer(text)})


def find_duplicate_proposition_ids(records: list[dict[str, Any]]) -> list[str]:
    """Detect proposition IDs reused across records with differing subjects.

    Each record needs `proposition_id` plus a subject field (`subject`,
    `proposition`, or `claim`). An ID appearing twice with the same normalized
    subject is a restatement; with different subjects it is a collision that
    breaks the ID→evidence link.
    """
    seen: dict[str, set[str]] = {}
    duplicates: list[str] = []
    for rec in records:
        pid = str(rec.get("proposition_id", "")).strip()
        if not pid:
            continue
        subject = (
            rec.get("subject") or rec.get("proposition") or rec.get("claim") or ""
        )
        normalized = re.sub(r"\s+", " ", str(subject)).strip().lower()[:120]
        subjects = seen.setdefault(pid, set())
        if normalized and subjects and normalized not in subjects:
            duplicates.append(pid)
        subjects.add(normalized)
    return sorted(set(duplicates))


def validate_debt_manifest(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate audit-manifest rows: unique IDs, enum work states, enum barriers.

    Returns a list of violation dicts; empty means valid. The common misuse this
    catches: free-text descriptions placed in the barrier_type column
    ("Full-index landscape statistics" instead of insufficient_search_completion).
    """
    violations: list[dict[str, Any]] = []
    dupes = set(find_duplicate_proposition_ids(entries))
    for i, entry in enumerate(entries):
        pid = entry.get("proposition_id", "")
        if pid in dupes:
            violations.append({
                "row": i, "proposition_id": pid,
                "violation": "duplicate proposition_id with different subject",
            })
        work_state = entry.get("work_state") or entry.get("state") or ""
        if work_state and work_state not in WORK_STATES:
            violations.append({
                "row": i, "proposition_id": pid,
                "violation": f"non-enum work_state: {work_state!r}",
            })
        barrier = entry.get("barrier_type", "")
        if barrier and barrier not in BARRIER_TYPES:
            violations.append({
                "row": i, "proposition_id": pid,
                "violation": f"barrier_type must be an enum value, got {barrier!r}",
            })
        if not barrier and work_state not in ("", "SEARCHING"):
            violations.append({
                "row": i, "proposition_id": pid,
                "violation": "missing barrier_type for unresolved proposition",
            })
    return violations


def scan_report(text: str, require_exec_sections: bool = True) -> IntegrityReport:
    """Run every text-level integrity scan against a rendered report."""
    report = IntegrityReport()
    report.placeholders = scan_placeholders(text)

    if require_exec_sections:
        report.missing_sections = [
            s for s in REQUIRED_EXEC_SECTIONS if s not in text
        ]

    # Extract audit-manifest tables from rendered text — but ONLY tables whose
    # header declares the fixed manifest schema. Historical/ledger tables with
    # different schemas (e.g. avenue ledgers keyed by proposition ID) are not
    # audit manifests and must not be validated against this vocabulary.
    def _is_separator(row_cells):
        return bool(row_cells) and all(
            set(c) <= {"-", ":", " "} and c for c in row_cells
        )

    manifest_rows: list[dict[str, Any]] = []
    header_cells: list[str] | None = None
    header_is_manifest = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            header_cells = None
            header_is_manifest = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if _is_separator(cells):
            continue
        lowered = [c.lower() for c in cells]
        first = (cells[0].split() or [""])[0] if cells else ""
        if _PROP_ID_RE.fullmatch(first):
            if header_is_manifest and len(cells) >= 4:
                manifest_rows.append({
                    "proposition_id": first,
                    "state": cells[1],
                    "barrier_type": cells[2],
                    "description": cells[3],
                })
            continue
        header_cells = cells
        header_is_manifest = (
            any("proposition" in c for c in lowered)
            and any("work state" in c for c in lowered)
            and any("barrier type" in c for c in lowered)
        )

    if manifest_rows:
        report.invalid_barriers = validate_debt_manifest(manifest_rows)
    else:
        # Fall back to scanning inline barrier mentions for enum conformance
        for match in re.finditer(
            r"[Bb]arrier type[:\s]*`?([a-z_]+)`?", text
        ):
            if match.group(1) not in BARRIER_TYPES:
                report.invalid_barriers.append({
                    "row": -1, "proposition_id": "",
                    "violation": f"unknown barrier_type: {match.group(1)!r}",
                })

    return report


def extract_proposition_ids(text: str) -> list[str]:
    """All proposition/avenue IDs mentioned in report order (deduplicated)."""
    seen: list[str] = []
    for m in _PROP_ID_RE.finditer(text):
        pid = m.group(0)
        if pid not in seen:
            seen.append(pid)
    return seen


PROPOSITION_LEGEND = """\
### Proposition Identifier Legend

| Pattern | Meaning | Example |
|---------|---------|---------|
| `P-<phase>-<seq>` | Proposition `<seq>` raised during phase `<phase>` | `P-07-001` — first market-analysis proposition |
| Letter suffix (`a`, `b`) | Sub-proposition derived from the base ID | `P-05-008a` |
| `A-<phase>-<seq>` | Search/evidence avenue attached to proposition | `A-02-004` |
| `R<n>` | Reviewed reference `<n>` | `R1`–`R6` |
| `C<n>` | Prospective claim grouping `<n>` | `C1`–`C3` |
| `C0`–`C4` | Mechanism-distance scale (identical → distant mechanism) | `C2` |
| `D0`–`D4` | Design-choice-distance scale (same domain → cross-domain leap) | `D3` |

Every proposition ID is unique across the entire report: one ID maps to exactly
one subject and its evidence trail. If two analyses touch the same question they
receive distinct IDs and cross-reference each other."""
