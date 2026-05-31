"""Scaffold for independent reproduction of research claims and simulations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReproductionPlan:
    """Minimal metadata required before reproducing a numerical or analytic claim."""

    claim_id: str
    recipe_path: str | None = None
    required_metadata: tuple[str, ...] = field(
        default_factory=lambda: (
            "geometry",
            "n_particles",
            "n_flux",
            "shift",
            "sector",
            "interaction_model",
            "solver",
            "tolerance",
            "seed",
            "commit_hash",
        )
    )

    def missing_metadata(self, metadata: dict) -> list[str]:
        """Return required reproducibility fields absent from a metadata dictionary."""
        return [key for key in self.required_metadata if metadata.get(key) in (None, "")]
