"""Scaffold for repository and result audit records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuditRecord:
    """Small immutable audit record for reproducibility and provenance checks."""

    target: str
    status: str
    message: str
    commit_hash: str | None = None

    def is_passing(self) -> bool:
        """Return True only for explicit passing audit records."""
        return self.status == "pass"
