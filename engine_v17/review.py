"""Independent review, fresh verification, and arbitration.

Critical rule: the agent that produces a material conclusion must not be
the sole authority validating that conclusion.

Workers produce structured observations/propositions/evidence references;
reviewers and verifiers receive enough structured evidence to independently
evaluate the result. Fake independence (same agent reviewing itself) is
prohibited — reviewer and verifier must be different agent instances from
the author and from each other.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ReviewVerdict(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"


@dataclass
class ReviewRecord:
    review_id: str
    proposition_id: str
    reviewer: str  # agent persona, e.g. ap-reviewer, ap-fresh-verifier
    author: str    # original author persona
    verdict: ReviewVerdict
    basis: str
    evidence_refs: list[str] = field(default_factory=list)
    barrier_type: str | None = None
    reviewed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_blind: bool = False  # fresh verifier is blind to author's verdict
    is_independent: bool = True  # must be different agent instance

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d

    def validate_independence(self, author_agent: str) -> list[str]:
        errors: list[str] = []
        if self.reviewer == author_agent:
            errors.append(f"reviewer {self.reviewer} is same as author {author_agent} — fake independence")
        if not self.is_independent:
            errors.append("is_independent must be True")
        if self.verdict == ReviewVerdict.PASSED and not self.evidence_refs:
            errors.append("passed review must cite evidence references")
        return errors


@dataclass
class ArbitrationRecord:
    arbitration_id: str
    proposition_id: str
    reviewer_record: ReviewRecord
    verifier_record: ReviewRecord
    arbiter: str  # ap-arbiter
    verdict: ReviewVerdict
    basis: str
    arbitrated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "arbitration_id": self.arbitration_id,
            "proposition_id": self.proposition_id,
            "reviewer_record": self.reviewer_record.to_dict(),
            "verifier_record": self.verifier_record.to_dict(),
            "arbiter": self.arbiter,
            "verdict": self.verdict.value,
            "basis": self.basis,
            "arbitrated_at": self.arbitrated_at,
        }


def independent_review(
    proposition_id: str,
    evidence_refs: list[str],
    author_agent: str,
    reviewer_agent: str = "ap-reviewer",
    basis: str = "",
    verdict: ReviewVerdict = ReviewVerdict.PASSED,
    barrier_type: str | None = None,
) -> ReviewRecord:
    """Create an independent review record. Caller must ensure reviewer != author."""
    record = ReviewRecord(
        review_id=f"REV-{proposition_id}-{hashlib.sha256((reviewer_agent+proposition_id).encode()).hexdigest()[:8]}",
        proposition_id=proposition_id,
        reviewer=reviewer_agent,
        author=author_agent,
        verdict=verdict,
        basis=basis or f"independent review of {proposition_id} by {reviewer_agent}",
        evidence_refs=evidence_refs,
        barrier_type=barrier_type,
        is_blind=False,
        is_independent=(reviewer_agent != author_agent),
    )
    errors = record.validate_independence(author_agent)
    if errors:
        raise ValueError(f"review independence violation: {errors}")
    return record


def fresh_verification(
    proposition_id: str,
    evidence_refs: list[str],
    author_agent: str,
    verifier_agent: str = "ap-fresh-verifier",
    basis: str = "",
    verdict: ReviewVerdict = ReviewVerdict.PASSED,
    barrier_type: str | None = None,
) -> ReviewRecord:
    """Create a blind fresh verification record. Verifier re-derives truth without reading author's verdict."""
    record = ReviewRecord(
        review_id=f"VER-{proposition_id}-{hashlib.sha256((verifier_agent+proposition_id).encode()).hexdigest()[:8]}",
        proposition_id=proposition_id,
        reviewer=verifier_agent,
        author=author_agent,
        verdict=verdict,
        basis=basis or f"fresh verification of {proposition_id} by {verifier_agent} (blind)",
        evidence_refs=evidence_refs,
        barrier_type=barrier_type,
        is_blind=True,
        is_independent=(verifier_agent != author_agent),
    )
    errors = record.validate_independence(author_agent)
    if errors:
        raise ValueError(f"verifier independence violation: {errors}")
    return record


def arbitrate(
    proposition_id: str,
    reviewer_record: ReviewRecord,
    verifier_record: ReviewRecord,
    arbiter_agent: str = "ap-arbiter",
    verdict: ReviewVerdict = ReviewVerdict.PASSED,
    basis: str = "",
) -> ArbitrationRecord:
    """Arbitrate when reviewer and verifier disagree.

    Arbiter decides technical forks and continues. It may not waive capability
    failure, open P0/P1 blockers, coverage failures, or real verification.
    """
    if reviewer_record.proposition_id != proposition_id or verifier_record.proposition_id != proposition_id:
        raise ValueError("arbitration proposition_id mismatch")
    if reviewer_record.verdict == verifier_record.verdict and verdict != reviewer_record.verdict:
        raise ValueError("arbiter verdict should match agreed reviewer/verifier verdict when they agree")
    return ArbitrationRecord(
        arbitration_id=f"ARB-{proposition_id}-{hashlib.sha256(proposition_id.encode()).hexdigest()[:8]}",
        proposition_id=proposition_id,
        reviewer_record=reviewer_record,
        verifier_record=verifier_record,
        arbiter=arbiter_agent,
        verdict=verdict,
        basis=basis or f"arbitration of {proposition_id}: reviewer={reviewer_record.verdict.value} verifier={verifier_record.verdict.value} → {verdict.value}",
    )


def write_review_ledger(
    reviews: list[ReviewRecord],
    arbitrations: list[ArbitrationRecord],
    output_dir: Path,
) -> Path:
    """Write review/verification/arbitration ledger to the evaluation directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger = {
        "reviews": [r.to_dict() for r in reviews],
        "arbitrations": [a.to_dict() for a in arbitrations],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = output_dir / "review-ledger.json"
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    return path
