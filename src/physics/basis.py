# File: src/physics/basis.py
"""Fermionic many-body basis construction and symmetry sorting for FQHE."""

import itertools
import logging

logger = logging.getLogger("physics.basis")

def state_to_occupation_string(state: int, n_orbitals: int) -> str:
    """Converts a bitmask integer state representation to a clean binary string |01101...>."""
    binary_str = bin(state)[2:].zfill(n_orbitals)[::-1] # reverse so orbit 0 is leftmost or rightmost
    # Let's write with standard leftmost being orbital 0
    return f"|{binary_str}>"

def build_lz_basis(n_particles: int, n_flux: int, target_lz: float = 0.0) -> list:
    """
    Constructs the fermionic many-body Hilbert space basis for a spherical geometry,
    conserving the total projection of angular momentum Lz.

    Args:
        n_particles (int): Number of fermions.
        n_flux (int): Number of magnetic flux quanta (monopoles). N_orbitals = N_flux + 1.
        target_lz (float): The total conserved Lz projection.

    Returns:
        list: Sorted list of integers representing many-body states as bitmasks.
    """
    n_orbitals = n_flux + 1

    # Check if target_lz is physically allowed. 
    # Lz = K - N * N_flux / 2  =>  K = Lz + N * N_flux / 2
    k_float = target_lz + n_particles * n_flux / 2.0
    if not k_float.is_integer():
        logger.error(f"Target Lz={target_lz} is not allowed for N={n_particles}, N_flux={n_flux}")
        raise ValueError(f"Lz={target_lz} must yield an integer index sum. (K = {k_float})")
        
    target_sum = int(k_float)
    basis = []

    # Iterate over all possible configurations
    for combo in itertools.combinations(range(n_orbitals), n_particles):
        if sum(combo) == target_sum:
            # Convert orbital combination to a bitmask integer (where bit i is orbital i)
            state = 0
            for orb in combo:
                state |= (1 << orb)
            basis.append(state)

    # Sort the basis states for fast binary search during matrix assembly
    basis.sort()
    logger.info(f"Constructed Lz={target_lz} basis for N={n_particles}, N_flux={n_flux}. Dimension: {len(basis)}")
    return basis

def build_disk_basis(n_particles: int, target_m: int) -> list:
    """
    Constructs the many-body basis for planar disk geometry, conserving total angular momentum M.

    Args:
        n_particles (int): Number of fermions.
        target_m (int): The total conserved angular momentum projection sum_i m_i.

    Returns:
        list: Sorted list of integers representing states.
    """
    # The maximum orbital index is bounded by target_m (since orbitals are non-negative on the disk)
    n_orbitals = target_m + 1
    basis = []
    
    for combo in itertools.combinations(range(n_orbitals), n_particles):
        if sum(combo) == target_m:
            state = 0
            for orb in combo:
                state |= (1 << orb)
            basis.append(state)
            
    basis.sort()
    logger.info(f"Constructed Disk basis for N={n_particles}, M={target_m}. Dimension: {len(basis)}")
    return basis
