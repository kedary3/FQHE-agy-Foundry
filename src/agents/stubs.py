"""Deterministic specialist agents used by local Magentic test mode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from src.agents.base import BaseAgent
from src.orchestrator.ledger import AgentReport, PlanStep, WorkflowState


def _claim(text: str, status: str, support: str, limitations: str) -> Dict[str, str]:
    return {
        "text": text,
        "epistemic_status": status,
        "support": support,
        "limitations": limitations,
    }


class LiteratureStubAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("literature", ["claims", "assumptions", "open_problems"])

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        return AgentReport(
            task_id=task.task_id,
            agent_name=self.name,
            assigned_goal=task.goal,
            summary="Reviewed candidate-state scope without promoting any candidate to settled status.",
            claims=[
                _claim(
                    "Pfaffian, anti-Pfaffian, PH-Pfaffian, CFL, and stripe/nematic descriptions remain hypotheses for this workflow.",
                    "phenomenological_argument",
                    "Project scientific scope requires hypothesis tracking across candidate states.",
                    "No literature corpus was queried in deterministic test mode.",
                )
            ],
            evidence=[
                {"type": "repository_context", "detail": "README and AGENTS scientific scope"}
            ],
            assumptions=["Deterministic test mode uses repository context instead of live literature search."],
            computations_performed=[],
            uncertainties=["Citation-level validation is deferred to production or curated fixtures."],
            recommended_next_tasks=["Add citation-backed summaries for the leading nu=5/2 candidate states."],
            epistemic_status=["phenomenological_argument", "unresolved"],
        )


class TheoryStubAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("theory", ["symmetry", "hamiltonians", "approximations"])

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        return AgentReport(
            task_id=task.task_id,
            agent_name=self.name,
            assigned_goal=task.goal,
            summary="Classified the fixture Hamiltonian statement separately from nu=5/2 extrapolations.",
            claims=[
                _claim(
                    "An exact diagonalization eigenvalue is exact only for the specified finite Hamiltonian and basis.",
                    "exact_result",
                    "This is a definition-level statement about a completely specified finite matrix problem.",
                    "It does not establish a thermodynamic or experimental conclusion.",
                ),
                _claim(
                    "Finite-width and Landau-level-mixing effects require explicit controlled parameters before acceptance.",
                    "controlled_approximation",
                    "Perturbative treatments need a stated expansion parameter and regime.",
                    "No expansion was evaluated in the stub.",
                ),
            ],
            evidence=[{"type": "epistemic_rule", "detail": "finite-size results are not thermodynamic proof"}],
            assumptions=["No live symbolic derivation was requested in test mode."],
            computations_performed=[],
            uncertainties=["Microscopic nu=5/2 Hamiltonian terms remain unresolved."],
            recommended_next_tasks=["Specify a second-Landau-level Hamiltonian with finite-width and LL-mixing terms."],
            epistemic_status=["exact_result", "controlled_approximation", "unresolved"],
        )


class NumericalEDStubAgent(BaseAgent):
    def __init__(self, fixture_path: Path | None = None) -> None:
        super().__init__("numerical_ed", ["exact_diagonalization", "fixtures"])
        self.fixture_path = fixture_path or Path("simulations/results/result_example_laughlin.json")

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        path = self.fixture_path
        evidence: List[Dict[str, object]] = []
        claims: List[Dict[str, str]] = []
        computations = []
        uncertainties = []

        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            eigenvalues = data["numerical"]["eigenvalues"]
            lowest = min(float(value) for value in eigenvalues)
            physics = data["physics"]
            metadata = data["metadata"]
            evidence.append(
                {
                    "type": "fixture",
                    "path": str(path),
                    "geometry": physics["geometry"],
                    "n_particles": physics["n_particles"],
                    "n_flux": physics["n_flux"],
                    "shift": physics["shift"],
                    "basis_dimension": physics["basis_dimension"],
                    "solver": metadata["solver"],
                    "lowest_eigenvalue": lowest,
                }
            )
            claims.append(
                _claim(
                    "The N=3, N_flux=6 Laughlin sphere fixture has a lowest eigenvalue consistent with zero.",
                    "numerical_evidence",
                    f"Fixture {path} reports lowest eigenvalue {lowest:.3e}.",
                    "This validates a small Laughlin fixture, not the nu=5/2 thermodynamic state.",
                )
            )
            computations.append("Loaded and checked the deterministic Laughlin validation fixture.")
        else:
            claims.append(
                _claim(
                    "The Laughlin validation fixture was not found.",
                    "unresolved",
                    f"Expected fixture path: {path}",
                    "Numerical validation cannot be completed until the fixture exists.",
                )
            )
            uncertainties.append("Missing fixture prevents ED validation.")

        return AgentReport(
            task_id=task.task_id,
            agent_name=self.name,
            assigned_goal=task.goal,
            summary="Checked deterministic ED fixture availability and lowest-eigenvalue evidence.",
            claims=claims,
            evidence=evidence,
            assumptions=["The fixture JSON is treated as a deterministic test artifact."],
            computations_performed=computations,
            uncertainties=uncertainties,
            recommended_next_tasks=["Add nu=5/2 second-Landau-level ED recipes with explicit geometry and shift."],
            epistemic_status=["numerical_evidence", "unresolved"],
        )


class WavefunctionTopologyStubAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("wavefunction_topology", ["trial_states", "topological_response"])

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        return AgentReport(
            task_id=task.task_id,
            agent_name=self.name,
            assigned_goal=task.goal,
            summary="Separated trial-state topology questions from fixture-level numerical validation.",
            claims=[
                _claim(
                    "Quasiparticle charge, braiding, and thermal Hall response remain discriminating tests for candidate nu=5/2 states.",
                    "conjecture",
                    "These are proposed next comparisons in the absence of live calculations.",
                    "No Berry phase, Chern number, or braiding computation was performed in test mode.",
                ),
                _claim(
                    "Trial wavefunction overlaps should be labeled as variational evidence unless the microscopic derivation is supplied.",
                    "variational_assumption",
                    "The workflow tracks trial-state assumptions explicitly.",
                    "No overlap calculation was performed in the stub.",
                ),
            ],
            evidence=[{"type": "workflow_scope", "detail": "topological observables are required physics targets"}],
            assumptions=["Candidate wavefunctions are hypotheses, not defaults."],
            computations_performed=[],
            uncertainties=["Topological response calculations remain unimplemented in deterministic test mode."],
            recommended_next_tasks=["Create fixtures for quasiparticle charge and shift predictions by candidate state."],
            epistemic_status=["conjecture", "variational_assumption", "unresolved"],
        )


class CriticStubAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("critic", ["falsification", "claim_review"])

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        return AgentReport(
            task_id=task.task_id,
            agent_name=self.name,
            assigned_goal=task.goal,
            summary="Flagged overinterpretation risks and next falsification targets.",
            claims=[
                _claim(
                    "The Laughlin fixture cannot be used as evidence for a specific nu=5/2 candidate ground state.",
                    "unresolved",
                    "The fixture is at N=3, N_flux=6 and validates reporting/ED plumbing only.",
                    "A nu=5/2 Hamiltonian and candidate comparison are still required.",
                )
            ],
            evidence=[{"type": "falsification_check", "detail": "fixture-to-target mismatch"}],
            assumptions=["Negative findings must be preserved in the final report."],
            computations_performed=["Reviewed reports already ingested into the progress ledger."],
            uncertainties=["No production-scale ED or experiment comparison has run."],
            recommended_next_tasks=["Define falsifiable candidate predictions for gap, charge, statistics, and PH symmetry."],
            epistemic_status=["unresolved"],
        )


class ReportStubAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("report", ["markdown_synthesis", "provenance"])

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        return AgentReport(
            task_id=task.task_id,
            agent_name=self.name,
            assigned_goal=task.goal,
            summary="Prepared final-report inputs from the manager-owned progress ledger.",
            claims=[
                _claim(
                    "The final report must preserve accepted, deferred, and unresolved claims with epistemic labels.",
                    "exact_result",
                    "This is an operational requirement of the repository workflow contract.",
                    "It is a process claim, not a physics result.",
                )
            ],
            evidence=[{"type": "ledger", "reports_ingested": len(state.progress_ledger.reports)}],
            assumptions=["The PI manager performs the final synthesis."],
            computations_performed=["Counted specialist reports in the progress ledger."],
            uncertainties=["Production citation formatting remains future work."],
            recommended_next_tasks=["Wire live report generation to validated agent artifacts."],
            epistemic_status=["exact_result", "unresolved"],
        )
