"""Minimal PI / Magentic Manager orchestration scaffold."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.agents.base import BaseAgent
from src.agents.stubs import (
    CriticStubAgent,
    LiteratureStubAgent,
    NumericalEDStubAgent,
    ReportStubAgent,
    TheoryStubAgent,
    WavefunctionTopologyStubAgent,
)
from src.orchestrator.ledger import AgentReport, PlanStep, WorkflowState
from src.orchestrator.memory import DurableMemoryCollector


class PIManager:
    """Manager-led Magentic loop with deterministic test-mode behavior."""

    def __init__(
        self,
        agents: Optional[Dict[str, BaseAgent]] = None,
        workspace_path: str | Path | None = None,
        github_client: object | None = None,
        max_rounds: int = 12,
        max_parallel_agents: int = 3,
        max_stall_count: int = 3,
        max_replans: int = 3,
    ) -> None:
        self.agents = agents or {
            "literature": LiteratureStubAgent(),
            "theory": TheoryStubAgent(),
            "numerical_ed": NumericalEDStubAgent(),
            "wavefunction_topology": WavefunctionTopologyStubAgent(),
            "critic": CriticStubAgent(),
            "report": ReportStubAgent(),
        }
        self.max_rounds = max_rounds
        self.max_parallel_agents = max_parallel_agents
        self.max_stall_count = max_stall_count
        self.max_replans = max_replans
        self.workspace_path = Path(workspace_path or Path.cwd()).resolve()
        self.github_client = github_client
        self.last_memory_context: Dict[str, object] = {}
        self.state: Optional[WorkflowState] = None

    def gather_facts(self, objective: str) -> List[str]:
        memory_context = self._collect_memory_context()
        signals = memory_context.get("planning_signals", {})
        facts = [
            f"Objective: {objective}",
            "Workflow type: Magentic manager-led orchestration, not a fixed sequence.",
            "Candidate nu=5/2 states are hypotheses and require evidence labels.",
            f"Durable memory sources indexed: {len(memory_context.get('source_index', []))}.",
            f"Prior required task failures in memory: {len(signals.get('prior_required_agent_failures', []))}.",
            f"Rejected claims in memory: {signals.get('rejected_claim_count', 0)}.",
        ]
        fixture_path = self.workspace_path / "simulations/results/result_example_laughlin.json"
        if fixture_path.exists():
            facts.append("Laughlin validation fixture is available under simulations/results/.")
        else:
            facts.append("Laughlin validation fixture is missing and must be treated as unresolved.")
        return facts

    def create_plan(self, objective: str) -> List[PlanStep]:
        memory_context = self._collect_memory_context()
        signals = memory_context.get("planning_signals", {})
        failures = signals.get("prior_required_agent_failures", [])
        next_actions = signals.get("pending_next_actions", [])
        assumptions = signals.get("unresolved_assumptions", [])
        fixtures = signals.get("validated_simulation_fixtures", [])
        trigger = self._compact_trigger(
            failures[:3] + next_actions[:3] + assumptions[:3]
        )
        fixture_summary = ", ".join(
            str(item.get("recipe_id") or item.get("path"))
            for item in fixtures[:3]
        ) or "no validated fixture recorded"
        return [
            PlanStep(
                task_id="task-literature",
                goal=(
                    "Daily command from durable memory: review claim-ledger gaps, "
                    "recent reports, and GitHub issue summaries to choose citation-bounded "
                    f"literature follow-up for objective '{objective}'."
                ),
                suggested_agent="literature",
                evidence_needed=["citations", "assumptions"],
                notes=[trigger],
            ),
            PlanStep(
                task_id="task-theory",
                goal=(
                    "Daily command from durable memory: convert unresolved assumptions "
                    "and rejected overclaims into exact or controlled analytical checks."
                ),
                suggested_agent="theory",
                evidence_needed=["epistemic_status"],
                notes=[trigger],
            ),
            PlanStep(
                task_id="task-numerical-ed",
                goal=(
                    "Daily command from durable memory: use simulation artifacts "
                    f"({fixture_summary}) to validate one bounded fixture or propose the "
                    "next small nu=5/2 ED recipe with finite-size caveats."
                ),
                suggested_agent="numerical_ed",
                evidence_needed=["fixture", "solver", "eigenvalues"],
                notes=[trigger],
            ),
            PlanStep(
                task_id="task-wavefunction-topology",
                goal=(
                    "Daily command from durable memory: identify topological observables "
                    "needed to distinguish candidate states already appearing in ledgers "
                    "or unresolved assumptions."
                ),
                suggested_agent="wavefunction_topology",
                dependencies=["task-literature", "task-theory"],
                evidence_needed=["quasiparticle_charge", "statistics"],
                notes=[trigger],
            ),
            PlanStep(
                task_id="task-critic",
                goal=(
                    "Daily command from durable memory: challenge the highest-risk "
                    "claim or repeated failure recorded in the falsification log, run "
                    "summaries, or issue state."
                ),
                suggested_agent="critic",
                dependencies=["task-numerical-ed"],
                evidence_needed=["failure_modes"],
                notes=[trigger],
            ),
            PlanStep(
                task_id="task-report",
                goal=(
                    "Daily command from durable memory: prepare synthesis inputs with "
                    "source provenance, unresolved gaps, and proposed ledger updates."
                ),
                suggested_agent="report",
                dependencies=[
                    "task-literature",
                    "task-theory",
                    "task-numerical-ed",
                    "task-wavefunction-topology",
                    "task-critic",
                ],
                evidence_needed=["report_sections"],
                notes=[trigger],
            ),
        ]

    def select_next_agents(self, state: WorkflowState) -> List[str]:
        selected: List[str] = []
        for step in state.task_ledger.next_ready_steps(limit=self.max_parallel_agents):
            agent_name = step.suggested_agent
            if agent_name in self.agents:
                state.task_ledger.assign_step_to_agent(step.task_id, agent_name)
                selected.append(agent_name)
        return selected

    def ingest_reports(self, reports: List[AgentReport]) -> None:
        if self.state is None:
            raise RuntimeError("PIManager.ingest_reports requires an active WorkflowState")
        for report in reports:
            self.state.ingest_agent_report(report)

    def should_replan(self, state: WorkflowState) -> bool:
        if state.progress_ledger.replan_count >= self.max_replans:
            return False
        return state.progress_ledger.detect_stall(
            state.task_ledger,
            max_stall_count=self.max_stall_count,
        )

    def replan(self, state: WorkflowState) -> List[PlanStep]:
        state.progress_ledger.request_replan("Progress stalled before all required tasks completed.")
        suffix = state.progress_ledger.replan_count
        pending_agents = [
            step.suggested_agent
            for step in state.task_ledger.plan_steps
            if step.status in {"pending", "failed"}
        ]
        new_step = PlanStep(
            task_id=f"task-replan-{suffix}",
            goal="Recover stalled Magentic progress by asking the critic to identify the blocking assumption.",
            suggested_agent="critic" if "critic" in self.agents else (pending_agents[0] if pending_agents else "report"),
            evidence_needed=["stall_reason", "next_action"],
        )
        state.task_ledger.add_plan_step(new_step)
        state.progress_ledger.clear_replan_request()
        return [new_step]

    def synthesize_final_report(self, state: WorkflowState) -> str:
        evidence_lines = []
        claim_lines = []
        contribution_lines = []
        next_tasks = []
        statuses = {
            "exact_result": [],
            "controlled_approximation": [],
            "numerical_evidence": [],
            "variational_assumption": [],
            "phenomenological_argument": [],
            "conjecture": [],
            "unresolved": [],
        }

        for report in state.progress_ledger.reports:
            contribution_lines.append(f"- {report.agent_name}: {report.summary}")
            for item in report.evidence:
                evidence_lines.append(f"- {report.agent_name}: {item}")
            for claim in report.claims:
                label = claim.get("epistemic_status", "unresolved")
                statuses.setdefault(label, []).append(claim.get("text", "Unspecified claim"))
                claim_lines.append(f"- `{label}`: {claim.get('text', 'Unspecified claim')}")
            next_tasks.extend(report.recommended_next_tasks)

        status_sections = []
        for label, items in statuses.items():
            status_sections.append(f"## {label}")
            if items:
                status_sections.extend(f"- {item}" for item in items)
            else:
                status_sections.append("- No claim accepted in this category during the test loop.")

        plan_lines = [
            f"- {step.task_id}: {step.goal} [{step.status}] agent={step.assigned_agent or step.suggested_agent}"
            for step in state.task_ledger.plan_steps
        ]
        report = "\n".join(
            [
                "# Objective",
                state.objective,
                "",
                "# Facts Gathered",
                *[f"- {fact}" for fact in state.progress_ledger.facts],
                "",
                "# Plan",
                *plan_lines,
                "",
                "# Agent Contributions",
                *(contribution_lines or ["- No agent reports were ingested."]),
                "",
                "# Evidence",
                *(evidence_lines or ["- No evidence returned."]),
                "",
                "# Physics Claim Classification",
                *(claim_lines or ["- No claims returned."]),
                "",
                *status_sections,
                "",
                "# Unresolved Gaps",
                f"- Stall count: {state.progress_ledger.stall_count}",
                f"- Replan count: {state.progress_ledger.replan_count}",
                "- Live literature citations, production LLM calls, and GitHub mutations are not used in deterministic test mode.",
                "",
                "# Recommended Next Tasks",
                *[f"- {task}" for task in dict.fromkeys(next_tasks)],
            ]
        )
        state.final_report = report
        return report

    def run_test_loop(self, objective: str) -> WorkflowState:
        state = WorkflowState.from_objective(objective=objective, mode="test")
        self.state = state
        state.status = "running"

        for fact in self.gather_facts(objective):
            state.add_fact(fact)
        state.add_plan_steps(self.create_plan(objective))

        for _round in range(self.max_rounds):
            selected_agents = self.select_next_agents(state)
            if not selected_agents:
                if state.task_ledger.is_complete():
                    break
                if self.should_replan(state):
                    self.replan(state)
                continue

            reports: List[AgentReport] = []
            for agent_name in selected_agents:
                task = next(
                    step
                    for step in state.task_ledger.plan_steps
                    if step.assigned_agent == agent_name and step.status == "in_progress"
                )
                reports.append(self.agents[agent_name].run(task, state))
            self.ingest_reports(reports)

            if self.should_replan(state):
                self.replan(state)

            if state.task_ledger.is_complete():
                break

        state.status = "completed" if state.task_ledger.is_complete() else "partial"
        self.synthesize_final_report(state)
        return state

    def _collect_memory_context(self) -> Dict[str, object]:
        collector = DurableMemoryCollector(
            workspace_path=self.workspace_path,
            mode="test",
            github_client=self.github_client,
        )
        self.last_memory_context = collector.collect()
        return self.last_memory_context

    @staticmethod
    def _compact_trigger(values: List[object]) -> str:
        compact = []
        seen = set()
        for value in values:
            text = str(value).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            compact.append(text)
        if not compact:
            return "memory_trigger: no prior blocking memory signal"
        return "memory_trigger: " + " | ".join(compact[:6])
