# File: tests/test_ed_validation.py
"""Physics validation and regression tests for FQHE Exact Diagonalization solver."""

import pytest
import numpy as np
from src.physics.basis import build_lz_basis
from src.physics.geometry.sphere import SphereGeometry
from src.physics.interactions import build_hamiltonian
from src.physics.diagonalization import diagonalize_hamiltonian

def test_basis_dimension():
    """Verify basis dimensions for standard FQHE systems on the sphere."""
    # N=3 particles, N_flux=6 (Laughlin filling 1/3)
    # Target Lz = 0 => index sum = 3 * 3 = 9
    basis = build_lz_basis(n_particles=3, n_flux=6, target_lz=0.0)
    # Expected combinations of 3 elements from range(7) summing to 9:
    # (0, 3, 6), (1, 2, 6), (1, 3, 5), (2, 3, 4), (0, 4, 5)
    # Total dimension = 5
    assert len(basis) == 5

def test_laughlin_ground_state():
    """
    Verify the Laughlin ground state for N=3, N_flux=6.
    Under the V1 Haldane pseudopotential (V1=1.0, others=0.0),
    the Laughlin state should be the zero-energy ground state.
    """
    n_particles = 3
    n_flux = 6
    target_lz = 0.0

    # Initialize geometry
    geom = SphereGeometry(n_particles=n_particles, n_flux=n_flux)
    geom.build_basis(target_lz=target_lz)

    # Set up Haldane pseudopotentials (only V1 is repulsive)
    # In our conventions, relative angular momentum j = 1, 3, 5...
    # V1 corresponds to relative angular momentum index j=1.
    pseudopotentials = {1: 1.0}

    # Build sparse Hamiltonian
    ham = build_hamiltonian(geom, pseudopotentials)

    # Solve for the ground state
    evals, evecs = diagonalize_hamiltonian(ham, k=1)

    # The ground state energy must be exactly 0 (within machine precision)
    # because Laughlin is the exact zero-energy density state of the V1 interaction.
    assert evals[0] == pytest.approx(0.0, abs=1e-10)
