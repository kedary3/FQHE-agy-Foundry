# File: src/physics/diagonalization.py
"""Lanczos sparse eigenvalue diagonalization for FQHE Hamiltonians."""

import logging
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

logger = logging.getLogger("physics.diagonalization")

def diagonalize_hamiltonian(ham: sp.csr_matrix, k: int = 3) -> tuple:
    """
    Computes the lowest k eigenvalues and eigenvectors of a sparse Hamiltonian.
    Falls back to dense diagonalization if the basis dimension is small.

    Args:
        ham (sp.csr_matrix): The sparse Hamiltonian matrix.
        k (int): Number of lowest eigenvalues to find.

    Returns:
        tuple: (eigenvalues, eigenvectors) where eigenvalues is an array and
               eigenvectors is a 2D array with eigenvectors as columns.
    """
    dim = ham.shape[0]
    
    # If the system is small, fall back to dense diagonalization
    if dim <= k + 1:
        logger.info(f"Basis size ({dim}) is small. Performing dense diagonalization.")
        dense_ham = ham.toarray()
        evals, evecs = np.linalg.eigh(dense_ham)
        # Sort and slice the lowest k
        idx = np.argsort(evals)
        evals = evals[idx][:k]
        evecs = evecs[:, idx][:, :k]
        return evals, evecs

    logger.info(f"Performing sparse Lanczos diagonalization for lowest {k} states of dimension {dim}.")
    try:
        # Use eigsh to find the lowest (Smallest Algebraic 'SA') eigenvalues
        evals, evecs = spla.eigsh(ham, k=k, which='SA')
        # Sort them explicitly to be absolutely sure they are ascending
        idx = np.argsort(evals)
        evals = evals[idx]
        evecs = evecs[:, idx]
        logger.info(f"Lanczos completed successfully. Ground state energy: {evals[0]:.8f}")
        return evals, evecs
    except Exception as e:
        logger.error(f"Sparse diagonalization failed: {e}. Attempting dense fallback.")
        dense_ham = ham.toarray()
        evals, evecs = np.linalg.eigh(dense_ham)
        idx = np.argsort(evals)
        evals = evals[idx][:k]
        evecs = evecs[:, idx][:, :k]
        return evals, evecs
