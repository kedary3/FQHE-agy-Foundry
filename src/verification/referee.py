"""Scaffold for referee checks before claims enter the accepted knowledge base."""

from __future__ import annotations

from dataclasses import dataclass


VALID_CLAIM_CLASSES = {
    "conjecture",
    "analytic_derivation",
    "numerical_evidence",
    "reproduced_numerical_evidence",
    "experimental_observation",
    "contradiction",
    "accepted_benchmark",
}


@dataclass(frozen=True)
class RefereeReport:
    """Structured referee decision without upgrading scientific claims implicitly."""

    claim_id: str
    claim_class: str
    approved: bool
    summary: str

    def validate(self) -> None:
        """Raise when a report uses an unsupported claim classification."""
        if self.claim_class not in VALID_CLAIM_CLASSES:
            valid = ", ".join(sorted(VALID_CLAIM_CLASSES))
            raise ValueError(f"Unsupported claim classification: {self.claim_class}. Valid classes: {valid}")
