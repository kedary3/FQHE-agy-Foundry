# File: src/physics/interactions.py
"""Fermionic second-quantized operators and Hamiltonian construction."""

import logging
import numpy as np
import scipy.sparse as sp
from .geometry.sphere import SphereGeometry

logger = logging.getLogger("physics.interactions")

def destroy_fermion(state: int, orbital: int) -> tuple:
    """
    Annihilate a fermion at the specified orbital.

    Args:
        state (int): Bitmask many-body state.
        orbital (int): Orbital index to destroy.

    Returns:
        tuple: (new_state, phase) where phase is 1 or -1. Returns (0, 0) if orbital is unoccupied.
    """
    if not (state & (1 << orbital)):
        return 0, 0

    # Count fermions in orbitals with index < orbital (bits to the right of the orbital bit)
    mask = (1 << orbital) - 1
    n_less = bin(state & mask).count('1')
    phase = -1 if (n_less % 2 != 0) else 1
    
    new_state = state ^ (1 << orbital)
    return new_state, phase

def create_fermion(state: int, orbital: int) -> tuple:
    """
    Create a fermion at the specified orbital.

    Args:
        state (int): Bitmask many-body state.
        orbital (int): Orbital index to create.

    Returns:
        tuple: (new_state, phase) where phase is 1 or -1. Returns (0, 0) if orbital is already occupied.
    """
    if state & (1 << orbital):
        return 0, 0

    mask = (1 << orbital) - 1
    n_less = bin(state & mask).count('1')
    phase = -1 if (n_less % 2 != 0) else 1
    
    new_state = state | (1 << orbital)
    return new_state, phase

def build_hamiltonian(geometry, pseudopotentials: dict) -> sp.csr_matrix:
    """
    Builds the sparse FQHE Hamiltonian matrix in the geometry's many-body basis.

    Args:
        geometry (Geometry): SphereGeometry (or other Geometry subclass) with constructed basis.
        pseudopotentials (dict): Dictionary mapping relative angular momentum index j to energy V_j.

    Returns:
        sp.csr_matrix: Sparse Hamiltonian in CSR format.
    """
    basis = geometry.basis
    dim = len(basis)
    n_orbitals = geometry.n_flux + 1

    # We will build the sparse matrix using the COO format lists (row, col, data)
    rows = []
    cols = []
    data = []

    logger.info(f"Assembling Hamiltonian matrix for basis dimension: {dim}")

    # To avoid double-computing and speed up assembly, precompute anti-symmetrized elements
    # V_anti[i, j, k, l] = <i, j | V_anti | k, l>
    # Since we only conserve Lz, we only compute elements where orb1 + orb2 == orb3 + orb4
    v_dict = {}
    
    # Loop over all possible orbital combinations
    for k in range(n_orbitals):
        for l in range(k + 1, n_orbitals):
            for i in range(n_orbitals):
                for j in range(i + 1, n_orbitals):
                    if (i + j) == (k + l):
                        # Use SphereGeometry anti-symmetrization method
                        if isinstance(geometry, SphereGeometry):
                            val = geometry.interaction_matrix_elements(i, j, k, l, pseudopotentials)
                        else:
                            # Direct/Exchange fallback
                            v_dir = geometry.matrix_element(i, j, k, l, pseudopotentials)
                            v_exc = geometry.matrix_element(i, j, l, k, pseudopotentials)
                            val = v_dir - v_exc

                        if abs(val) > 1e-12:
                            v_dict[(i, j, k, l)] = val

    # Convert basis to dict for O(1) index lookups
    basis_lookup = {state: idx for idx, state in enumerate(basis)}

    # Apply H to every state in the basis
    # H = sum_{i < j, k < l} V_anti[i, j, k, l] c_i^\dagger c_j^\dagger c_l c_k
    for col_idx, state in enumerate(basis):
        for (i, j, k, l), v_val in v_dict.items():
            # Destroy k, then l
            s1, p1 = destroy_fermion(state, k)
            if p1 == 0:
                continue
            s2, p2 = destroy_fermion(s1, l)
            if p2 == 0:
                continue

            # Create j, then i
            s3, p3 = create_fermion(s2, j)
            if p3 == 0:
                continue
            s4, p4 = create_fermion(s3, i)
            if p4 == 0:
                continue

            # If the resulting state is in our symmetry basis
            if s4 in basis_lookup:
                row_idx = basis_lookup[s4]
                phase = p1 * p2 * p3 * p4
                rows.append(row_idx)
                cols.append(col_idx)
                data.append(phase * v_val)

    # Construct the sparse matrix in CSR format
    ham = sp.coo_matrix((data, (rows, cols)), shape=(dim, dim)).tocsr()
    logger.info("Successfully constructed sparse Hamiltonian.")
    return ham
