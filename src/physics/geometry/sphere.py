# File: src/physics/geometry/sphere.py
"""Spherical geometry implementation for FQHE exact diagonalization."""

import logging
import functools
from .base import Geometry
from ..basis import build_lz_basis

logger = logging.getLogger("physics.geometry.sphere")

class SphereGeometry(Geometry):
    def __init__(self, n_particles: int, n_flux: int, shift: int = 3):
        """
        Initializes the FQHE Sphere Geometry.

        Args:
            n_particles (int): Number of particles.
            n_flux (int): Flux quanta.
            shift (int): Geometry shift (e.g. shift = 3 for Moore-Read state, shift = 1 for Laughlin).
        """
        super().__init__(n_particles, n_flux, shift)
        self.s = n_flux / 2.0  # Monopole strength (spin-representation S)
        self._cg_cache = {}

    def build_basis(self, target_lz: float = 0.0) -> list:
        """Constructs the fermionic many-body basis in the conserved Lz sector."""
        self.basis = build_lz_basis(self.n_particles, self.n_flux, target_lz)
        return self.basis

    @functools.lru_cache(maxsize=10000)
    def _get_cg(self, j1, m1, j2, m2, j3, m3):
        """Helper to compute and cache Clebsch-Gordan coefficients using SymPy."""
        try:
            from sympy.physics.wigner import clebsch_gordan
            # SymPy clebsch_gordan expects Rational or float/integer types
            val = float(clebsch_gordan(j1, j2, j3, m1, m2, m3))
            return val
        except ImportError:
            # Fallback if sympy is not available (analytical approximation or error)
            raise ImportError("SymPy is required to calculate spherical FQHE matrix elements.")

    def matrix_element(self, orb1: int, orb2: int, orb3: int, orb4: int, pseudopotentials: dict) -> float:
        """
        Computes the unsymmetrized matrix element <orb1, orb2 | V | orb3, orb4> on a sphere.
        Orbital index 'i' corresponds to single-particle Lz component m_i = i - N_flux/2.
        """
        m1 = orb1 - self.s
        m2 = orb2 - self.s
        m3 = orb3 - self.s
        m4 = orb4 - self.s

        # Lz conservation check
        if abs((m1 + m2) - (m3 + m4)) > 1e-9:
            return 0.0

        M = m1 + m2
        elem_sum = 0.0

        # L ranges from |S-S| to S+S, i.e., 0 to 2*S (which is N_flux)
        # S is the monopole strength self.s
        for L_int in range(int(2 * self.s) + 1):
            L = float(L_int)
            # Relative angular momentum index j_rel = 2*S - L
            j_rel = int(2 * self.s - L)

            # Only include terms with defined pseudopotentials
            if j_rel not in pseudopotentials:
                continue

            v_j = pseudopotentials[j_rel]
            if abs(v_j) < 1e-12:
                continue

            # Clebsch-Gordan coefficients <S, m1; S, m2 | L, M>
            cg1 = self._get_cg(self.s, m1, self.s, m2, L, M)
            cg2 = self._get_cg(self.s, m3, self.s, m4, L, M)

            elem_sum += cg1 * cg2 * v_j

        return elem_sum

    def interaction_matrix_elements(self, orb1: int, orb2: int, orb3: int, orb4: int, pseudopotentials: dict) -> float:
        """
        Computes the anti-symmetrized fermionic matrix element:
        V_anti = <orb1, orb2 | V | orb3, orb4> - <orb1, orb2 | V | orb4, orb3>
        """
        v_direct = self.matrix_element(orb1, orb2, orb3, orb4, pseudopotentials)
        v_exchange = self.matrix_element(orb1, orb2, orb4, orb3, pseudopotentials)
        return v_direct - v_exchange

    def get_symmetry_sectors(self) -> list:
        """Returns the single global conserved Lz sector. Multi-sector sorting can be implemented here."""
        # By default, we work in the single target basis constructed
        return [list(range(len(self.basis)))]
