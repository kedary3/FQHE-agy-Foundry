import json
from pathlib import Path

import pytest


FIXTURE_PATH = Path("simulations/results/result_example_laughlin.json")


def test_laughlin_result_json_fixture_schema():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert data["recipe_id"]
    assert data["physics"]["geometry"]
    assert data["physics"]["n_particles"]
    assert data["physics"]["n_flux"]
    assert data["numerical"]["eigenvalues"]
    assert data["metadata"]["status"] == "success"


def test_laughlin_lowest_eigenvalue_is_zero_with_tolerance():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    lowest = min(float(value) for value in data["numerical"]["eigenvalues"])

    assert lowest == pytest.approx(0.0, abs=1e-10)


def test_laughlin_solver_metadata_exists():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert data["metadata"]["solver"] == "scipy.sparse.linalg.eigsh"
