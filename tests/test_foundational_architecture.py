from pathlib import Path

import pytest

from src.physics.geometry.base import Geometry
from src.orchestrator import cli
from src.verification.referee import RefereeReport


WORKSPACE = Path(__file__).resolve().parents[1]


def test_geometry_base_interface_exists():
    geom = Geometry(n_particles=2, n_flux=3, shift=1)

    assert geom.n_particles == 2
    assert geom.n_flux == 3
    assert geom.shift == 1
    with pytest.raises(NotImplementedError):
        geom.build_basis()
    with pytest.raises(NotImplementedError):
        geom.matrix_element(0, 1, 1, 0, interaction={})
    with pytest.raises(NotImplementedError):
        geom.get_symmetry_sectors()


def test_knowledge_base_scaffold_directories_exist():
    for relative_path in (
        "knowledge_base/hypotheses",
        "knowledge_base/contradictions",
        "knowledge_base/benchmarks",
        "knowledge_base/decisions",
    ):
        assert (WORKSPACE / relative_path).is_dir()


def test_referee_claim_classification_is_conservative():
    report = RefereeReport(
        claim_id="H-TEST",
        claim_class="numerical_evidence",
        approved=False,
        summary="Small-system evidence only.",
    )
    report.validate()

    invalid = RefereeReport(
        claim_id="H-TEST",
        claim_class="truth",
        approved=True,
        summary="Invalid upgrade.",
    )
    with pytest.raises(ValueError, match="Unsupported claim classification"):
        invalid.validate()


def test_provider_connectivity_cli_does_not_print_secret(monkeypatch, capsys):
    class FakeAdapter:
        provider = "gemini"

        def __init__(self, provider=None):
            self.provider = provider or "gemini"

        def generate_text(self, prompt, system_instruction=None, model=None):
            return "OK"

    monkeypatch.setenv("GEMINI_API_KEY", "super_secret_token")
    monkeypatch.setattr(cli, "LLMAdapter", FakeAdapter)
    monkeypatch.setattr("sys.argv", ["orchestrator", "--check-provider", "--provider", "gemini"])

    cli.main()

    output = capsys.readouterr()
    assert "Provider connectivity status: ok" in output.out
    assert "super_secret_token" not in output.out
    assert "super_secret_token" not in output.err
