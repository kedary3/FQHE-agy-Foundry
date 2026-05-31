# File: src/physics/geometry/base.py
"""Abstract Base Class defining the geometry space of FQHE simulations."""

class Geometry:
    def __init__(self, n_particles: int, n_flux: int, shift: int = 0):
        """
        Initialize the physical geometry parameters.

        Args:
            n_particles (int): Number of particles.
            n_flux (int): Number of flux quanta (monopoles/magnetic orbitals).
            shift (int): Geometry shift parameter (e.g. shift = 3 for Moore-Read on sphere).
        """
        self.n_particles = n_particles
        self.n_flux = n_flux
        self.shift = shift
        self.basis = []

    def build_basis(self) -> list:
        """
        Constructs the fermionic many-body basis in conserved symmetry sectors.

        Returns:
            list: List of many-body states (typically represented as integers).
        """
        raise NotImplementedError("Each physical geometry must implement its own build_basis method.")

    def matrix_element(self, orb1: int, orb2: int, orb3: int, orb4: int, interaction) -> float:
        """
        Computes the 2-body interaction matrix element <orb1, orb2 | V | orb3, orb4>.

        Args:
            orb1, orb2, orb3, orb4 (int): Orbital indices.
            interaction: Interaction parameters or Haldane pseudopotentials.

        Returns:
            float: Matrix element value.
        """
        raise NotImplementedError("Each physical geometry must implement its own matrix_element calculation.")

    def get_symmetry_sectors(self) -> list:
        """
        Decomposes the full Hilbert space into disjoint symmetry blocks.

        Returns:
            list: List of symmetry sectors, each containing basis state indices.
        """
        raise NotImplementedError("Each physical geometry must implement its own get_symmetry_sectors decomposition.")
