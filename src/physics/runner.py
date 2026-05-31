# File: src/physics/runner.py
"""Declarative Simulation Recipe compiler and execution harness."""

import yaml
import json
import os
import logging
import numpy as np
from .geometry.sphere import SphereGeometry
from .interactions import build_hamiltonian
from .diagonalization import diagonalize_hamiltonian

logger = logging.getLogger("physics.runner")

def execute_simulation_recipe(recipe_path: str, output_dir: str = None) -> dict:
    """
    Parses a declarative simulation recipe YAML file, runs the physical ED solver,
    and returns/saves the structured results.

    Args:
        recipe_path (str): Path to the simulation recipe YAML file.
        output_dir (str): Optional directory to save output JSON results.

    Returns:
        dict: Complete execution results with eigenvalues, basis dimensions, and metadata.
    """
    logger.info(f"Loading simulation recipe from: {recipe_path}")
    
    with open(recipe_path, 'r') as f:
        recipe = yaml.safe_load(f)

    # Parse physics configuration
    phys_cfg = recipe.get("physics", {})
    geometry_type = phys_cfg.get("geometry", "sphere").lower()
    n_particles = int(phys_cfg.get("n_particles"))
    n_flux = int(phys_cfg.get("n_flux"))
    shift = int(phys_cfg.get("shift", 0))
    target_lz = float(phys_cfg.get("target_lz", 0.0))

    # Interaction details
    interaction_cfg = phys_cfg.get("interaction", {})
    # Parse pseudopotentials keys as integers
    raw_pseudos = interaction_cfg.get("pseudopotentials", {})
    pseudopotentials = {int(k): float(v) for k, v in raw_pseudos.items()}

    # Numerical settings
    num_cfg = recipe.get("numerical", {})
    k_lowest = int(num_cfg.get("k_lowest", 3))

    logger.info(f"Starting simulation run: {recipe.get('id', 'anonymous')} - {recipe.get('title', '')}")
    logger.info(f"System: N={n_particles}, N_flux={n_flux}, Geometry={geometry_type}, Lz={target_lz}")

    # Geometry instantiation
    if geometry_type == "sphere":
        geom = SphereGeometry(n_particles=n_particles, n_flux=n_flux, shift=shift)
    else:
        raise ValueError(f"Unsupported geometry type in recipe: {geometry_type}")

    # Step 1: Hilbert space basis construction
    geom.build_basis(target_lz=target_lz)
    dim = len(geom.basis)

    # Step 2: Hamiltonian assembly
    ham = build_hamiltonian(geom, pseudopotentials)

    # Step 3: Sparse Lanczos Diagonalization
    evals, evecs = diagonalize_hamiltonian(ham, k=k_lowest)

    # Compile result dictionary
    results = {
        "recipe_id": recipe.get("id"),
        "title": recipe.get("title"),
        "physics": {
            "geometry": geometry_type,
            "n_particles": n_particles,
            "n_flux": n_flux,
            "shift": shift,
            "target_lz": target_lz,
            "basis_dimension": dim,
            "pseudopotentials": pseudopotentials
        },
        "numerical": {
            "k_lowest": k_lowest,
            "eigenvalues": evals.tolist()
        },
        "metadata": {
            "status": "success",
            "solver": "scipy.sparse.linalg.eigsh"
        }
    }

    # Save to file if output_dir is provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        out_filename = f"result_{recipe.get('id', 'run')}.json"
        out_path = os.path.join(output_dir, out_filename)
        with open(out_path, 'w') as out_f:
            json.dump(results, out_f, indent=2)
        logger.info(f"Saved simulation results to {out_path}")

    return results
